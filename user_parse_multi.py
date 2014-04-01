import os

def findUsers(page, starting=0, increment=1):
	file = open("Cache/"+page+"_likers.htm")
	users = []
	for line in file:
		if (line[-14:] == 'browse_search\n'):
			users.append(line)

	#clean up duplicates using set
	users = set(users)
	usernames = []
	if not os.path.isfile("User Likes/"+page+"/user_likes.txt"):
		fp = open("User Likes/"+page+"/users_likes.txt", "w")
		for i in users:
			username = i.split("/")[3].split("?")[0]
			usernames.append(username)
			fp.write(username + "\n")

		fp.close()
	else:
		fp = open("User Likes/"+page+"/users_likes.txt", "r")
		for line in fp:
			if (line.rstrip() == "profile.php"):
				continue

			usernames.append(line.rstrip())

	fp.close()

	if (increment == 1):
		return usernames
	else:
		return usernames[starting::increment]