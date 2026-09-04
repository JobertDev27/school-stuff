import express from "express"

const server = express()

server.set("views engine", "ejs")
server.use(express.json())

server.get("/", (req, res) => {
    res.send("Hello world")
})

server.listen(4000, () => {
    console.log("Hello from port 4000")
})
