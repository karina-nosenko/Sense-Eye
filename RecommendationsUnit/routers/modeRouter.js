const { Router } = require('express');
const { modeController } = require('../controllers/modeController');

const modeRouter = new Router();

modeRouter.post('/singlePlayerMode', modeController.singlePlayerMode);
modeRouter.post('/sameTeamModeA', modeController.sameTeamModeA);
modeRouter.post('/sameTeamModeB', modeController.sameTeamModeB);
modeRouter.post('/differentTeamsModeA', modeController.differentTeamsModeA);
modeRouter.post('/differentTeamsModeB', modeController.differentTeamsModeB);
modeRouter.post('/fullGameMode', modeController.fullGameMode);
modeRouter.post('/alertCloseToGate', modeController.alertCloseToGate);

module.exports = { modeRouter };