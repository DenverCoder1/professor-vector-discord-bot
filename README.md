# Professor Vector Discord Bot

[![Powered by Nextcord](https://custom-icon-badges.herokuapp.com/badge/-Powered%20by%20Nextcord-0d1620?logo=nextcord)](https://github.com/nextcord/nextcord "Powered by Nextcord Python API Wrapper")

Discord bot for r/Arithmancy - A reddit feed bot and more!

## ⏰ Triggers and Tasks

When a new submission is posted in r/Arithmancy, it will be shared in #announcements

If there is an active countdown in #announcements, it will be updated every minute.

The countdown is activated by including a date enclosed in `!!` within a message (ex. `!!23 May 2pm EDT!! until the puzzle ends!`)

## 🗄️ Commands (Archivist Role Only)

`!createchannel <channel-name>` - create a channel with the given name in the same category

`!movechannel <category-name>` - move the current channel to the category with the given name

`!solved` - add the solved prefix to a channel name (ex. "channel" becomes "solved-channel")

`!unsolved` - remove the solved prefix from a channel name (ex. "solved-channel" becomes "channel")

## 🧑‍💼 Commands (Admin only)

`!resend [message-id]` - resend the last announcement (in case changes have been made), optionally edit an existing message.

`!lockcategory <category-name>` - Lock `@everyone` from writing in a given category
