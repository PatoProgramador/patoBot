const { Distube } = require('distube');

module.exports = (client) => {
    client.distube = new Distube(client, {
        emitNewSongOnlye: false,
        leaveOnEmpty: true,
        leaveOnFinish: true,
        leaveOnStop: true,
        savePreviousSongs: true,
        emitAddSongWhenCreatingQueue: false,
        searchSongs: 0,
        nsfw: false,
        emptyCooldown: 25,
        ytdlOptions: {
            highWaterMark: 1024 * 1024 * 64,
            quality: "highestaudio",
            format: "audioonly",
            liveBuffer: 60000,
            dlChunkSize: 1024 * 1024 * 4
        },
        youtubeDL: false,
        plugins: [
            new SpotifyPlugin({
                parallel: true,
                emitEventsAfterFetching: true
            })
        ]
    })
};