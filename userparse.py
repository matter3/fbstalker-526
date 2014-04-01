import os

def find_users(page, starting=0, increment=1):

	#Open the downloaded cache of all page likers and add them to array
	file = open("Cache/"+page+"_likers.htm")
	users = []
	for line in file:
		if (line[-14:] == 'browse_search\n'):
			users.append(line)

	#clean up duplicates using set
	users = set(users)
	usernames = []

	#Create file needed to store all users who like page if does not exist
	if not os.path.isfile("User Likes/"+page+"/user_likes.txt"):
		fp = open("User Likes/"+page+"/users_likes.txt", "w")

		for i in users:
			username = i.split("/")[3].split("?")[0]
			usernames.append(username)
			fp.write(username + "\n")

		fp.close()
	else:

		#Else the file does exist and we can load it and extract users
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