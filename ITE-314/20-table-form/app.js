import express from "express"
import {db} from "./db/db.js"

const server = express()

server.set("view engine", "ejs")

server.use(express.urlencoded({ extended: true }));
server.use(express.json())
server.use(express.static("public"))

server.get("/", (req, res) => {
    res.render("index")
})

server.get("/users", async (req, res) => {
    const [rows] = await db.query("SELECT * FROM biodata");

    res.render("users", {
        users: rows
    });
});

server.post("/add_table", async (req, res) => {
    const {
	first_name,
	middle_name,
	last_name,
	birth_date,
	age,
	gender,
	civil_status,
	nationality,
	religion,
	address,
	city,
	province,
	phone,
	email,
	student_id,
	course,
	year_level,
	school,
	emergency_contact,
	emergency_phone,
    } = req.body;

    try {
	await db.execute(
	    `INSERT INTO biodata (
first_name, middle_name, last_name, birth_date, age,
gender, civil_status, nationality, religion, address,
city, province, phone, email, student_id, course,
year_level, school, emergency_contact, emergency_phone
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
	    [
		first_name, middle_name, last_name, birth_date, age,
		gender, civil_status, nationality, religion, address,
		city, province, phone, email, student_id, course,
		year_level, school, emergency_contact, emergency_phone
	    ]
	);

	res.send("User added successfully");
    } catch (error) {
	console.error(error);
	res.status(500).send("Failed to add user");
    }
});

server.listen(4000, () => {
    console.log("Hello from port 4000")
})
