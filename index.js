const Discord  = require('discord.js');
require('dotenv').config();

const bot = new Discord.Client({ intents: [131071]});

bot.commands = new Discord.Collection();
bot.aliases = new Discord.Collection();

function requestHandlers() {
    ["command", "events"].forEach(handler => {
        try {
            require(`./handlers/${handler}`)(bot, Discord)
        } catch (error) {
            console.warn(error)
        }
    })
}
requestHandlers();

bot
    .login(process.env.DS_BOT_TOKEN)
    .then(() => {
        console.log(`El ${bot.user.username} se ha iniciado :)`)
        bot.user.setActivity('existir');
    })
    .catch((err) => console.log(err));
