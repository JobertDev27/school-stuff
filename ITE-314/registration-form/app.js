const express = require('express')
const {conn} = require('./conn')

const app = express()

app.set('view engine', 'ejs')

app.use(express.json())
app.use(express.urlencoded({ extended: false }));
app.use(express.static('public'))

app.get('/', (req, res) => {
    res.render('index')
})

app.post('/register', (req, res) => {
    const fname = req.body.fname
    const lname = req.body.lname
    const email = req.body.email
    const pass = req.body.pass
    const address = req.body.address
    const cnumber = req.body.cnumber

const query = `INSERT INTO boardmates VALUES( 0, '${fname}', '${lname}', '${address}', '${email}', '${pass}', ${cnumber});`;

    conn.query(query, (err, result) => {
	if (err) throw err;
	res.send(`<script>alert('user successfully created!'); window.location.href='/';</script>`)
    })
})

app.listen(4000, () => {
    console.log('Server live on port: 4000')
})
