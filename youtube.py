# -*- coding: utf-8 -*-

# Sample Python code for youtube.channels.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python

import os
import json
import csv

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]


def main():
    # SCRIPT SETUP
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secret_958615982309-f47dm2vaqghjj5c1q8aj2si2t2ck6etp.apps.googleusercontent.com.json"

    credential_path = os.path.join('./', 'credential_sample.json')
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(client_secrets_file, scopes)
        credentials = tools.run_flow(flow, store)


    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    # SCRIPT METHODS
    # get_video_list_page --- input: Next page token, output: list of videos
    def get_video_list_page(next_page_token):
        request = youtube.playlistItems().list(
            part="snippet",
            fields="nextPageToken,items(snippet(title,resourceId(videoId)))",
            maxResults=50,
            playlistId="UUt7fwAhXDy3oNFTAzF2o8Pw",
            pageToken=next_page_token
        )
        return request.execute()

    # get_more_data -- input: reviews dictionary, output: info and stats for each review
    def get_more_data(reviews):
        request = youtube.videos().list(
            part="snippet,statistics",
            fields="items(snippet(title,publishedAt,description)),items(statistics(viewCount,likeCount,dislikeCount,commentCount))",
            id=','.join([reviews[review]['URL'] for review in reviews])
        )
        return request.execute()

    # print_json --- input: python object, output: void, pretty prints JSON
    def print_json(obj):
        json_formatted_str = json.dumps(obj, indent=2)
        print(json_formatted_str)

    # filter_reviews -- input: list of items (review videos), output: list of videos with only reviews
    def filter_reviews(videos):
        return [review['snippet'] for review in list(filter(
            lambda x: 'yunoreview' not in x['snippet']['title'].lower() and
            'track review' not in x['snippet']['title'].lower() and
            ('review' in x['snippet']['title'].lower() or
            'not good' in x['snippet']['title'].lower()),
            videos['items']
        ))]

    # find_score -- input: description string, output: list of words with '/10' (scores)
    def find_score(description):
        if 'NOT GOOD' in description or 'NOTGOOD' in description:
            return ['NOT GOOD/10']
        return list(filter((lambda word: '/10' in word and 'http' not in word), description.split()))

    # get_title_artist_type -- input: video title string, output: dict with artist, title, type
    def get_title_artist_type(title_string):
        TYPES = ['album', 'mixtape', 'ep', 'redux', 'compilation', 'playlist']
        info = {'artist': '', 'title': '', 'type': ''}

        title_split = title_string.split('- ')
        info['artist'] = title_split[0]
        album_title = title_split[1].split(' ')
        lower_title = list(map(lambda x: x.lower(), album_title))
        review_idx = lower_title.index('review')

        if any(x in lower_title[review_idx - 1] for x in TYPES):
            info['type'] = album_title[review_idx - 1]
            info['title'] = ' '.join(album_title[:review_idx - 1])
        else:
            info['title'] = ' '.join(album_title[:review_idx])
            info['type'] = None
        
        return info

    
    # SCRIPT START
    next_page_token = ""

    # current batch of reviews, to be written to csv
    current_reviews = {}

    with open('db.csv', 'w', newline='') as csvfile:
        # set up CSV fields
        fieldnames = ['title', 'URL', 'publishedAt', 'viewCount', 'likeCount', 'dislikeCount', 'commentCount', 'description', 'score', 'artist', 'album', 'type']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # loop while we haven't ran out of video lists
        while next_page_token != False:
            # query youtube for videos (with URLS) and filter out non-reviews
            video_list = get_video_list_page(next_page_token)
            video_items = filter_reviews(video_list)

            # add URLs to reviews dict
            for video in video_items:
                current_reviews[video['title']] = {'URL': video['resourceId']['videoId']}

            # get more info (like description and statistics) from youtube from URLS
            extra_items = get_more_data(current_reviews)

            # add info to reviews dict
            for review in extra_items['items']:
                current_reviews[review['snippet']['title']]['publishedAt'] = review['snippet']['publishedAt']
                current_reviews[review['snippet']['title']]['description'] = review['snippet']['description']
                try:
                    current_reviews[review['snippet']['title']]['viewCount'] = review['statistics']['viewCount']
                except KeyError:
                    current_reviews[review['snippet']['title']]['viewCount'] = 'No view count'
                current_reviews[review['snippet']['title']]['likeCount'] = review['statistics']['likeCount']
                current_reviews[review['snippet']['title']]['dislikeCount'] = review['statistics']['dislikeCount']
                current_reviews[review['snippet']['title']]['commentCount'] = review['statistics']['commentCount']
                # Find score and add score to current_reviews 
                score = find_score(review['snippet']['description'])
                current_reviews[review['snippet']['title']]['score'] = score
                try:
                    title_info = get_title_artist_type(review['snippet']['title'])
                    current_reviews[review['snippet']['title']]['artist'] = title_info['artist']
                    current_reviews[review['snippet']['title']]['album'] = title_info['title']
                    current_reviews[review['snippet']['title']]['type'] = title_info['type']
                except (IndexError, ValueError) as e:
                    current_reviews[review['snippet']['title']]['artist'] = e
                    current_reviews[review['snippet']['title']]['album'] = e
                    current_reviews[review['snippet']['title']]['type'] = e
            
            for review in current_reviews:
                writer.writerow({
                    'title': review,
                    'URL': current_reviews[review]['URL'],
                    'publishedAt': current_reviews[review]['publishedAt'],
                    'viewCount': current_reviews[review]['viewCount'],
                    'likeCount': current_reviews[review]['likeCount'],
                    'dislikeCount': current_reviews[review]['dislikeCount'],
                    'commentCount': current_reviews[review]['commentCount'],
                    'description': current_reviews[review]['description'].replace("\n", " ").replace("\n\n", " ").replace("\r", " "),
                    'score': current_reviews[review]['score'],
                    'artist': current_reviews[review]['artist'],
                    'album': current_reviews[review]['album'],
                    'type': current_reviews[review]['type']
                })

            # set next_page_token
            try:
                next_page_token = video_list['nextPageToken']
            except KeyError:
                next_page_token = False

            # reset current_reviews for new loop
            current_reviews = {}

        print('ALL DONE!!')
        # SCRIPT END

if __name__ == "__main__":
    main()