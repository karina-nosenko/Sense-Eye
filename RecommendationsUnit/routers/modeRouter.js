const { Router } = require('express');
const { modeController } = require('../controllers/modeController');

const userRouter = new Router();

userRouter.post('/', usersController.addUser); 

module.exports = { userRouter };