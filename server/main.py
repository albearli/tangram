'''
Backend API Server to connect to MySQL and Neo4j databases (hosted on AWS).
'''
from flask import Flask, jsonify, request
from flask_cors import CORS
import config
import json
import mysql.connector
import secrets
import neo4j_api

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

'''
Config for database secrets is not saved in the repo (only locally)
'''
mysqlSecrets = config.mysqlKey
neo4jSecrets = config.neo4jKey

try:
    connection = mysql.connector.connect(
        host=mysqlSecrets['host'],
        user=mysqlSecrets['user'],
        password=mysqlSecrets['password'],
        database=mysqlSecrets['database']
    )
except mysql.connector.Error as e:
    print('Ran into mysql exception: {}'.format(e))

@app.route('/')
def home():
    return 'Connected to server'

@app.route('/max-likes')
def userWithMostLikes():
    '''
    Select user with most likes
    '''
    cur = connection.cursor()
    try:
        cur.execute(
            'SELECT u.Username, u.totLikes FROM (SELECT x.Username, count(x.likes) AS totLikes FROM tangram_users JOIN tangram_posts AS x ON tangram_users.Username = x.Username GROUP BY x.Username) AS u HAVING u.totLikes = max(u.totLikes) ORDER BY u.totLikes DESC'
        )
        headers = [x[0] for x in cur.description]
        result = [dict(zip(headers, row)) for row in cur.fetchall()]
        cur.close()
        return json.dumps(result)
    except mysql.connector.Error as e:
        cur.close()
        print('Ran into exception: {}'.format(e))

@app.route('/average-users')
def usersWithPopularPosts():
    '''
    Select users with average likes of >= 5
    '''
    cur = connection.cursor()
    try:
        cur.execute(
           'SELECT u.Username, count(p.Likes) AS totLikes FROM tangram_users u JOIN tangram_posts p ON u.Username = p.Username GROUP BY u.Username HAVING avg(p.likes) >= 5 ORDER BY totLikes DESC' 
        )
        headers = [x[0] for x in cur.description]
        result = [dict(zip(headers, row)) for row in cur.fetchall()]
        cur.close()
        return json.dumps(result)
    except mysql.connector.Error as e:
        cur.close()
        print('Ran into exception: {}'.format(e))

@app.route('/get-user/<string:username>')
def getUser(username):
    '''
    Get specific user based on username from MySQL
    '''
    cur = connection.cursor()
    try:
        cur.execute("SELECT * FROM tangram_users, ((select distinct U2.user1 AS Friends FROM tangram_friends AS U1 INNER JOIN tangram_friends AS U2 ON U1.user1 = U2.user2 WHERE U1.user1 = '{}') UNION (select distinct U1.user2 AS Friends FROM tangram_friends AS U1 INNER JOIN tangram_friends AS U2 ON U1.user1 = U2.user2 WHERE U1.user1 = '{}')) AS C WHERE tangram_users.Username = '{}'".format(username, username, username))
        headers = [x[0] for x in cur.description]
        result = [dict(zip(headers, row)) for row in cur.fetchall()]
        cur.close()
        arr = []
        for i in range(len(result)):
            arr.append(result[i]['Friends'])
        reformatted = {
            "Username" : result[0]['Username'],
            "Name" : result[0]['Name'],
            "TotalLikes" : result[0]['TotalLikes'],
            "ProfilePicture" : result[0]['ProfilePicture'],
            "Description" : result[0]['Description'],
            "Friends" : arr

        }
        return json.dumps(reformatted)
    except mysql.connector.Error as e:
        cur.close()
        print('Ran into exception: {}'.format(e))

@app.route('/get-friends/<string:username>')
def getFriends(username):
    '''
    Get friends of specific user based on username from MySQL
    '''
    cur = connection.cursor()
    try:
        cur.execute("(select distinct U2.user1 AS Friend FROM tangram_friends AS U1 INNER JOIN tangram_friends AS U2 ON U1.user1 = U2.user2 WHERE U1.user1 = '{}') UNION (select distinct U1.user2 AS Friend FROM tangram_friends AS U1 INNER JOIN tangram_friends AS U2 ON U1.user1 = U2.user2 WHERE U1.user1 = '{}')".format(username, username))
        headers = [x[0] for x in cur.description]
        result = [dict(zip(headers, row)) for row in cur.fetchall()]
        cur.close()
        return json.dumps(result)
    except mysql.connector.Error as e:
        cur.close()
        print('Ran into exception: {}'.format(e))

@app.route('/get-all-users')
def getAllUsers():
    '''
    Get all users from `tangram_users` table from MySQL DB
    '''
    cur = connection.cursor()
    try:
        cur.execute("SELECT * FROM tangram_users")
        headers = [x[0] for x in cur.description]
        result = [dict(zip(headers, row)) for row in cur.fetchall()]
        cur.close()
        return json.dumps(result)
    except mysql.connector.Error as e:
        cur.close()
        print('Ran into exception: {}'.format(e))

@app.route('/create-user', methods=['POST'])
def createUser():
    '''
    Create a user in the users table in MySQL.
    Body: "Username"
    '''
    print(request.get_json())
    username = request.get_json()['Username']
    desc = request.get_json()['Description']
    name = request.get_json()['Name']

    cur = connection.cursor()
    try:
        cur.execute("INSERT INTO tangram_users(Username, Name, Description, TotalLikes, ProfilePicture) VALUES ('{}', '{}', '{}', {}, {})".format(username, name, desc, 0, 'NULL'))
        connection.commit()
        connection.commit()
        cur.close()
        return json.dumps([{ 'Status' : 1 }])
    except mysql.connector.Error as e:
        cur.close()
        print('Ran into exception: {}'.format(e))

@app.route('/add-friend', methods=['POST'])
def addFriend():
    '''
    Adds friends in the friends table in MySQL.
    '''
    print(request.get_json())
    user1 = request.get_json()['user1']
    user2 = request.get_json()['user2']
    user1 = str(user1)
    user2 = str(user2)

    if(user1 > user2):
        temp = user1
        user1 = user2
        user2 = temp

    cur = connection.cursor()
    try:
        cur.execute("INSERT INTO tangram_friends(user1, user2) VALUES ('{}', '{}')".format(user1, user2))
        connection.commit()
        connection.commit()
        cur.close()
        return json.dumps([{ 'Status' : 1 }])
    except mysql.connector.Error as e:
        cur.close()
        print('Ran into exception: {}'.format(e))

@app.route('/delete-friend', methods=['DELETE'])
def deleteFriend():
    '''
    Delete friend from `friends` table given the username
    '''
    user1 = request.get_json()['user1']
    user2 = request.get_json()['user2']
    user1 = str(user1)
    user2 = str(user2)
    cur = connection.cursor()
    try:
        cur.execute("DELETE FROM tangram_friends where user1 = '{}' AND user2 = '{}'".format(user1, user2))
        connection.commit()
        cur.close()
        return 'Successfully deleted friends: {}, {}'.format(user1, user2)
    except mysql.connector.Error as e:
        cur.close()
        print('Ran into exception: {}'.format(e))
    
@app.route('/delete-user', methods=['DELETE'])
def deleteUser():
    '''
    Delete user from `users` table given the username
    '''
    username = request.args['Username']
    cur = connection.cursor()
    try:
        cur.execute("DELETE FROM tangram_users where username = '{}'".format(username))
        connection.commit()
        cur.close()
        return 'Successfully deleted user: {}'.format(username)
    except mysql.connector.Error as e:
        cur.close()
        print('Ran into exception: {}'.format(e))
    
@app.route('/update-description', methods=['PUT'])
def updateDescription():
    '''
    Update a user's description (250 characters) based on username
    '''
    print(request.get_json())
    username = request.get_json()['Username']
    desc = request.get_json()['Description']

    cur = connection.cursor()
    try:
        cur.execute("UPDATE tangram_users SET Description = '{}' WHERE Username = '{}';".format(desc, username))
        connection.commit()
        cur.close()
        return 'Successfully updated user: {}'.format(username)
    except mysql.connector.Error as e:
        cur.close()
        print('Ran into exception: {}'.format(e))

@app.route('/get-post/<string:PostID>')
def getPost(PostID):
    '''
    Get specific post from neo4j
    '''
    return neo4j_api.get_specific_video(PostID)

@app.route('/get-post-by-coordinates/<string:x>/<string:y>')
def getPostByCoordinate(x, y):
    '''
    Get specific post from neo4j based on coordinate
    '''
    return neo4j_api.get_video_by_coordinates(x, y)

@app.route('/get-all-posts')
def getAllPosts():
    '''
    Get all posts from neo4j db
    '''
    return neo4j_api.get_all_videos()

@app.route('/create-post', methods=['POST'])
def createPost():
    '''
    Create a post to neo4j
    Params: text, videoURL, XCoordinate, YCoordinate, Timestamp, Username
    '''
    postID = secrets.token_hex(nbytes=16) # random hash for unique PostIDs
    text = request.get_json()['text']
    videoURL = request.get_json()['videoURL']
    XCoordinate = request.get_json()['XCoordinate']
    YCoordinate = request.get_json()['YCoordinate']
    TimeStamp = request.get_json()['Timestamp']
    username = request.get_json()['Username']

    result = neo4j_api.create_post(postID, text, videoURL, XCoordinate, YCoordinate, TimeStamp, username)
    return json.dumps([{'Status' : result }])

@app.route('/delete-post/<string:PostID>', methods=['DELETE'])
def deletePost(PostID):
    '''
    Delete specific post from neo4j based on PostID
    '''
    result = neo4j_api.delete_post(PostID)
    print(result)
    return json.dumps([{'Status' : result}])
    

@app.route('/update-post-likes/<string:PostID>', methods=['PUT'])
def updatePostLikes(PostID):
    '''
    Update the likes on a post based on PostID
    '''
    likes = request.form['totalLikes']
    result = neo4j_api.delete_post(PostID, likes)
    return json.dumps([{'Status' : result}])

@app.route('/update-post-title/<string:PostID>', methods=['PUT'])
def updatePostTitle(PostID):
    '''
    Update the title on a post based on PostID
    '''
    title = request.form['title']
    result = neo4j_api.updatePostTitle(PostID, title)
    print(result)
    return json.dumps([{'Status' : result}])

@app.route('/update-post-coordinates/<string:PostID>', methods=['PUT'])
def updatePostCoordinates(PostID):
    '''
    Update the x and y coordinates on a post based on PostID
    '''
    x = request.form['XCoordinate']
    y = request.form['YCoordinate']
    result = neo4j_api.update_post_coordinates(PostID, x, y)
    print(result)
    return json.dumps([{'Status' : result}])
    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
