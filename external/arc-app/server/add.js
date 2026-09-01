const MongoClient = require('mongodb').MongoClient;
const assert = require('assert');
const fs = require('fs');
const path = require('path');

// Load MONGODB_URI from the arc-app root .env regardless of CWD (see .env.example).
require('dotenv').config({ path: path.resolve(__dirname, '../.env') });

// Connection URL
const url = process.env.MONGODB_URI;
if (!url) {
    console.error('MONGODB_URI is required. Set it in the environment or in external/arc-app/.env (see .env.example).');
    process.exit(1);
}
const data_dir = '../client/src/fixed_data';
var files = fs.readdirSync(data_dir);
var data = []
for(i = 0; i < files.length; i++) {
    var full_path = path.resolve(__dirname, data_dir, files[i])
    console.log(full_path);
    let rawdata = fs.readFileSync(full_path);
    data.push(JSON.parse(rawdata));
}


// Use connect method to connect to the Server
MongoClient.connect(url, function(err, client) {
    const db = client.db('problems');
    const problemCollection = db.collection('problems');
    problemCollection.deleteMany({})
        .then(res => {
            problemCollection.insertMany(data)
                .then(res => {
                    console.log("success");
                    client.close();
                });
        })
        .catch(err => console.log(err));
});
