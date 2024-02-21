# extracts text and emoji from youtube live chat

from ytdl_updated import livechat_to_csv

if __name__ == "__main__":

    print("Enter file path to live chat file: ")
    livechat_file = input()

    livechat_csv = livechat_to_csv(livechat_file)
    print(f"Live chat saved as: {livechat_csv}")
