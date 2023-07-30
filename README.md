# youtubeCommentScrapper

The objective of this project is to build a program that can scrape more than 10k comments on YouTube.

## Challenges

A simple program using Selenium to scroll down pages and scrape comments on YouTube will reach a maximum number of collectable comments at approximately 3,000 comments. This limitation is a result of the memory-saving algorithm that removes comments from the view to free up space for loading additional comments.

## Objective

Build a program that can scrape more than 10k comments on YouTube.

- Language: Python
- Core libraries: Pandas, Selenium
- Parameters: number_of_comments, youtube_video_url
- Output: youtubeComments.csv
- Requirements: when number_of_comments > 10k, len(youtubeComments) can be in 8k ~ 12k

## Algorithms

There are currently three algorithms (methods) in the project: **Simple**, **Batched**, and **Expensive**. Below explains the three methods.

### Simple

The **Simple** method involves scrolling down to the view's end to load comments X times, where X is a function of the number of comments the user wants to scrape. After scrolling X times to the end, the program will click "Read more" and then gradually scroll up to the top to load and display the full comments. Finally, the program will scrape all the comments in the view.

### Batched

The **Batched** method doesn't scroll directly to the view's end all at once. Instead, it scrolls 80 times to the end in each batch. After each batch, it clicks "Read more", scrolls up, and then proceeds to scrape the comments. The program will repeat this batched process X times.

The value of X is calculated as follows:

$$ X=Y//80 $$

Here, Y represents the total number of times to scroll to the end, based on the number of comments the user wishes to scrape.

### Expensive

The **Expensive** method is based on the assumption that the Batched method may omit comments due to the unpredictable length of the view after clicking "Read more". To mitigate this, the Expensive method runs the process of scrolling down, scrolling up, and scraping comments multiple times to minimize the chances of missing any comments. Before exiting, the program will remove duplicates to ensure the collected comments are unique.

## Result

Unfortunately, the current progress has not achieved its objective. The value of len(youtubeComments) still heavily relies on the total number of comments, leading to imprecise output for the parameter. Besides, there is still a maximum number of collectible comments, which seems to be stuck at around 8,000 comments.

Here are the statistics showing how many comments I was able to obtain by running the program. "Sample" represents the number of comments that were successfully scraped. "Population" represents the total number of comments available on YouTube for the video. The "Method" column indicates the method used during the scraping process. It is important to note that the program was instructed to scrape 10,000 comments for each video.

| video                                           | sample | population | method   |
|-------------------------------------------------|-------:|-----------:|---------:|
| KAACHI - Your Turn                             |   8056 |     101068 | expensive|
| BLACKSWAN - Tonight                            |   5716 |      56394 | expensive|
| EXP EDITION - FEEL LIKE THIS Korean Reaction!  |   4554 |      18239 | expensive|
| SB19 - Alab                                    |   3925 |     130759 | expensive|
| Bling Bling - G.G.B                            |   3895 |      11060 | expensive|
| Cherry Bullet - QA                             |   3813 |      21456 | expensive|
| EXP EDITION - Feel Like This                   |   3648 |      14704 | expensive|
| wooah - wooah                                  |   2444 |       4942 | expensive|
| kpoper reacts to SB19                          |   2160 |       3457 | expensive|
| KAACHI MV REACTION - KOREABOO                  |   2074 |       3000 | expensive|
| FANATICS - SUNDAY                              |   1577 |       2532 | expensive|
| riVerse Reacts Tonight by BLACKSWAN            |    846 |        948 | expensive|
| The Kulture Study FANATICS Sunday MV           |    193 |        203 | expensive|
| Cherry Bullet QA Reaction                      |    109 |        112 | expensive|
| wooah - wooah MV Reaction                      |     54 |         54 | expensive|
| REACTION to BLING BLING - G.G.B OFFICIAL MV    |     15 |         16 | simple   |
