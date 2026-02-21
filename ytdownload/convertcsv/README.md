# README

To use `convertcsv.py`:

1. Copy the livechat from an ongoing stream.
2. Save it as a text file and put it into the same directory as the program.
3. Run `python convertcsv.py`.
4. Enter the name of the text file when prompted.
5. The program saves the CSV in the same directory and prints the output filename.

## CSV columns

- timestamp - Chat message timestamp captured from the transcript.
- user - Username handle (typically starting with `@`).
- membership - Membership badge text such as “Member (2 months)” or “New member”.
- member_status - Extended status details like “Member for 12 months”, when present.
- member_tier - Membership tier label such as “Support Group Members”, when provided.
- dollar_amount - Donation amount for Super Chats or similar paid messages.
- message - Combined text of the chat message body.

### user

**Haven't tested** with live chat that doesn't include the username with an `@`. 

## Superchat .99 vs .00

Superchat ends in .99 if it was donated from iOS. Ends in .00 if it was another platform.

Source: <https://www.reddit.com/r/youtube/comments/buww7o/why_do_so_many_smart_chat_donations_end_in_99/>
