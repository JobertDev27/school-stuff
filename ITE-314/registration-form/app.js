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

app.get('/login', (req, res) => {
    res.render('login')
})

app.post('/get-account', (req, res) => {
    const email = req.body.email
    const pass = req.body.pass

    const query = `SELECT * FROM boardmates WHERE email = '${email}' AND pass = '${pass}';`
    conn.query(query, (err, result) => {
	if (err) throw err;
	if (result.length > 0) {
	    res.send(`<script>alert("login successfully"); window.location.href="/";</script>`)
	} else {
	 res.send(`<script>alert("Wrong credentials"); window.location.href="login";</script>`)
	}
    })
})

app.listen(4000, () => {
    console.log('Server live on port: 4000')
})
