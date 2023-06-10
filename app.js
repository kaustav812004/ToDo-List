//jshint esversio:6

const express = require('express');
const bodyParser = require("body-parser");
const date = require(__dirname + "/date.js");

const app = express();


const items = ["Buy Food", "Cook Food", "Eat Food"];
const workitems = [];

app.set('view engine', 'ejs');

app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static("public"));

app.get('/', (req, res) => {
    
    const day =  date.getDay();

    res.render("list", {
        ListTitle: day, newListItems: items
    })
});

app.post("/", (req, res) => {

    const item = req.body.newItem;

    if (req.body.list === "work") {
        workitems.push(item);
        res.redirect("/work");
    }
    else {
        items.push(item);
        res.redirect("/");
    }



    items.push(item);

    res.redirect("/");

})

app.get("/work", (req, res) => {
    res.render("list", {
        ListTitle: "Work List", newListItems: workitems
    });
});

app.post("/work", (req, res) => {
    console.log(req.body);
    const item = req.body.newItem;
    workitems.push(item);
    res.redirect("/WORK");
});

app.listen(3000, () => {
    console.log("Server is  running on port: 3000");
});

//We can push an elememnt in an array after decllaring an array as constant but can't declare a new elememt