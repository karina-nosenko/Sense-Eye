const express = require('express');

const { modeRouter } = require('./routers/modeRouter');

const app = express();
const port = process.env.PORT || 8080;

if(process.env.ENV === 'development') {
    const logger = require('morgan');
    app.use(logger('dev'));
}

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use('/api/singlePlayerMode', modeRouter);
app.use('/api/sameTeamModeA', modeRouter);
app.use('/api/sameTeamModeB', modeRouter);
app.use('/api/differentTeamsModeA', modeRouter);
app.use('/api/differentTeamsModeB', modeRouter);
app.use('/api/fullGameMode', modeRouter);

app.use('*', (req, res) => {
    res.status(404).json({'error': 'Page Not Found'});
});

app.listen(port, () => {
    console.log(`Listening on port ${port}`);
});