const { Client } = require('discord.js');
require('dotenv').config();

const bot = new Client({ intents: [131071]});

bot.login(process.env.DS_BOT_TOKEN).then(() => {
    console.log(`El bot ${bot.user.username} se ha iniciado :)`)
    bot.user.setActivity('Mimiendo');
}).catch((err) => console.log(err));
