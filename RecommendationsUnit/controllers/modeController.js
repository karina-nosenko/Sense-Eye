const { MAX_goal_PASSING_DISTANCE,
        MIN_goal_PASSING_DISTANCE,
        MAX_TEAMMATE_PASSING_DISTANCE,
        MIN_TEAMMATE_PASSING_DISTANCE,
        MAX_OPPONENT_DISTANCE } = require('../constants');

const isBetween = (thing, min, max) => {
    return (thing >= min) && (thing <= max);
}

const calculateDistanceToGoal = (player, goal) => {
    // TODO
    return 1; 
}

const getPlayerWithBall = (players) => {
    // TODO
    return 1;
}

const getTeammate = (ballHolder, players) => {
    // TODO
    return 1;
}

const calculateEuclideanDistance = (ballHolder, teammate) => {
    // TODO
    return 1;
}

const pathToGoalIsFree = (ballHolder, teammate, goals) => {
    // TODO
    return 1;
}

const recommendMovingAwayFromGoal = (res, player, goal) => {
    // TODO
    res.status(200).json({ "success": "recommendMovingAwayFromGoal" });
}

const recommendMovingTowardsGoal = (res, player, goal) => {
    // TODO
    res.status(200).json({ "success": "recommendMovingTowardsGoal" });
}

const recommendDirectShotOnGoal = (res, player, goal) => {
    // TODO
    res.status(200).json({ "success": "recommendDirectShotOnGoal" });
}

const recommendPassToTeammate = (res, ballHolder, teammate) => {
    // TODO
    res.status(200).json({ "success": "recommendPassToTeammate" });
}

const recommendKeepTheBall = (res) => {
    // TODO
    res.status(200).json({ "success": "recommendKeepTheBall" });
}

exports.modeController = {
    singlePlayerMode(req, res) {
        const { body } = req;

        const goalDistance = calculateDistanceToGoal(body.players[0], body.goals[0]);
        if (goalDistance <= MIN_goal_PASSING_DISTANCE) {
            recommendMovingAwayFromGoal(res, body.players[0], body.goals[0]);
        } else if (goalDistance >= MAX_goal_PASSING_DISTANCE) {
            recommendMovingTowardsGoal(res, body.players[0], body.goals[0]);
        } else {
            recommendDirectShotOnGoal(res, body.players[0], body.goals[0]);
        } 
    },
    sameTeamModeA(req, res) {
        const { body } = req;

        ballHolder = getPlayerWithBall(body.players);
        teammate = getTeammate(ballHolder, body.players);
        teammateDistance = calculateEuclideanDistance(ballHolder, teammate);
        goalDistance = calculateDistanceToGoal(ballHolder, body.goals);

        if (isBetween(goalDistance, MIN_goal_PASSING_DISTANCE, MAX_goal_PASSING_DISTANCE) &&
            pathToGoalIsFree(ballHolder, teammate, body.goals)) {
            recommendDirectShotOnGoal(res, body.players[0], body.goals[0]);
        } else if (isBetween(teammateDistance, MIN_TEAMMATE_PASSING_DISTANCE, MAX_TEAMMATE_PASSING_DISTANCE)) {
            recommendPassToTeammate(res, ballHolder, teammate);
        } else {
            recommendKeepTheBall(res);
        }
    },
    sameTeamModeB(req, res) {
        const { body } = req;

        res.status(200).json({ "success": "success" });
    },
    differentTeamsModeA(req, res) {
        const { body } = req;

        res.status(200).json({ "success": "success" });
    },
    differentTeamsModeB(req, res) {
        const { body } = req;

        res.status(200).json({ "success": "success" });
    },
    fullGameMode(req, res) {
        const { body } = req;

        res.status(200).json({ "success": "success" });
    },
}