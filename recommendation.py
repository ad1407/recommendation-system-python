from math import sqrt
#from numpy import square
# A dictionary of movie critics and their ratings of a small
# set of movies
critics = {'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5,
'The Night Listener': 3.0},
'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5,
'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0,
'You, Me and Dupree': 3.5},
'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
'Superman Returns': 3.5, 'The Night Listener': 4.0},
'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
'The Night Listener': 4.5, 'Superman Returns': 4.0,
'You, Me and Dupree': 2.5},
'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
'You, Me and Dupree': 2.0},
'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
'Toby': {'Snakes on a Plane':4.5, 'You, Me and Dupree':1.0, 'Superman Returns':4.0}}

# Returns a distance-based similarity score for person1 and person2
def sim_distance(prefs, person1, person2):
	# Get list of shared items
	si = {}
	for item in prefs[person1]:
		if item in prefs[person2]:
			si[item] = 1

	# if they have no ratings in common, return 0
	if len(si) == 0: 
		return 0
	
# 	squares = []
# 	for item in prefs[person1]:
# 		if item in prefs[person2]:
# 			squares.append(pow(prefs[person1][item] - prefs[person2][item], 2))
			
	sum_of_squares = sum([pow(prefs[person1][item] - prefs[person2][item], 2) 
						for item in prefs[person1] if item in prefs[person2]])
	
	return 1/(1 + sum_of_squares)

#print(sim_distance(critics, 'Lisa Rose', 'Gene Seymour'))


# Returns the Pearson correlation coefficient for p1 and p2

def sim_pearson(prefs, p1,p2):
	# Get the list of mutually rated items
	si = {}
	for item in prefs[p1]:
		if item in prefs[p2]:
			si[item] = 1
	
	n = len(si)
	
	if n == 0: return 0
	
	# Add up all the preferences
	sum1 = sum([prefs[p1][item] for item in si])
	sum2 = sum([prefs[p2][item] for item in si])
	
	# Sum up the squares 
	sum1Sq = sum([pow(prefs[p1][item],2) for item in si])
	sum2Sq = sum([pow(prefs[p2][item],2) for item in si])
	
	# Sum up the products
	pSum = sum([prefs[p1][item] * prefs[p2][item] for item in si])
	
	# Calculate Pearson score
	num=pSum - (sum1*sum2/n)
	den=sqrt((sum1Sq-pow(sum1,2)/n)*(sum2Sq-pow(sum2,2)/n))
	if den == 0: return 0
	
	r = num/den
	return r

#print(sim_pearson(critics, 'Lisa Rose', 'Gene Seymour'))

# Returns the best matches for the person from the prefs dictionary
# Number of results and similarity function are optional params
def topMatches(prefs, person, n=5, similarity=sim_pearson):
	scores=[(similarity(prefs, person, other), other)
						for other in prefs if other != person]
	
	# Sort the list so the highest scores appear at the top
	scores.sort(reverse=True)
	return scores[0:n]

#print(topMatches(critics, 'Toby', n=3))

# Gets recommendations for a person by using weighted average
# of every other user's ranking
def getRecommendations(prefs, person, similarity=sim_pearson):
	totals = {}
	simSums = {}
	
	for other in prefs:
		# Don't compare me to myself
		if other == person: continue
		sim=similarity(prefs, person, other)
		
		# Ignore scores of zero or lower
		if sim<=0: continue
		for item in prefs[other]:
			# only score movies which I haven't seen yet
			if item not in prefs[person] or prefs[person][item] == 0:
				# Similarity * Score
				totals.setdefault(item, 0)
				totals[item] += prefs[other][item]*sim
				# Sum of similarities
				simSums.setdefault(item,0)
				simSums[item] += sim
	
	# Create the normalized list
	rankings = [(total/simSums[item], item) for item,total in totals.items()]
	
	# Return the sorted list
	rankings.sort(reverse=True)
	return rankings

#print(getRecommendations(critics, 'Toby'))

def transformPref(prefs):
	result = {}
	for person in prefs:
		for item in prefs[person]:
			result.setdefault(item, {})
			
			# Flip item and preson
			result[item][person] = prefs[person][item]
	return result


def calculateSimilarItems(prefs, n=10):
	# Create a dictionary of items showing which other items they
	# are more similar to.
	result = {}
	
	# Invert the preference matrix to be item-centric
	itemPrefs = transformPref(prefs)
	c=0
	for item in itemPrefs:
		# Status updates for large datasets
		c+=1
		if c%100==0: print("%d / %d" % (c, len(itemPrefs)))
		# Find the most similar items to this one
		scores=topMatches(itemPrefs, item, n=n, similarity=sim_distance)
		result[item] = scores
	return result

#itemMatch = calculateSimilarItems(critics) 
#print(itemMatch)

def getRecommendedItems(prefs, itemMatch, user):
	userRatings=prefs[user]
	scores = {}
	totalSim={}
	
	# Loop over items rated by this user
	for (item, rating) in userRatings.items():
		
		#Loop over items similar to this one
		for (similarity, item2) in itemMatch[item]:
			
			#Ignore if this user has already rated this item
			if item2 in userRatings: continue
			
			# Weighted sum of rating times cosine_similarity
			scores.setdefault(item2,0)
			scores[item2]+=similarity*rating
			
			# Sum of all the similarities
			totalSim.setdefault(item2, 0)
			totalSim[item2]+= similarity
		
	# Divide each total score by total weighting to get an average
	ranking=[(score/totalSim[item],item) for item,score in scores.items()]
	
	# Return the ranking from highest to lowest
	ranking.sort(reverse=True)
	return ranking

#print(getRecommendedItems(critics, itemMatch, 'Toby'))

def loadMovieLens(path='ml-100k'):
	
	# Get movie titles
	movies={}
	for line in open(path+'/u.item'):
		(id, title)=line.split('|')[0:2]
		movies[id]=title
	
	# Load data
	prefs={}
	for line in open(path+'/u.data'):
		(user,movieid, rating, ts)=line.split('\t')
		prefs.setdefault(user, {})
		prefs[user][movies[movieid]]=float(rating)
	return prefs

prefs=loadMovieLens()
#print(prefs['87'])
#print(getRecommendations(prefs, '87')[0:30])

itemsim = calculateSimilarItems(prefs, n=50)
print(getRecommendedItems(prefs, itemsim, '87')[0:30])