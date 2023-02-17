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

app.use('/api/mode', modeRouter);

app.use('*', (req, res) => {
    res.status(404).json({'error': 'Page Not Found'});
});

app.listen(port, () => {
    console.log(`Listening on port ${port}`);
});

process.on('SIGINT', () => {
    console.log('Shutting down server...');
    process.exit(0);
  });