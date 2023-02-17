const { MAX_GOAL_PASSING_DISTANCE,
        MIN_GOAL_PASSING_DISTANCE,
        MAX_TEAMMATE_PASSING_DISTANCE,
        MIN_TEAMMATE_PASSING_DISTANCE,
        MAX_OPPONENT_DISTANCE } = require('../constants');

const isBetween = (thing, min, max) => {
    return (thing >= min) && (thing <= max);
}

const calculateEuclideanDistance = (x1, y1, x2, y2) => {
    return Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
}

const calculateDistanceToGoal = (player, goals) => {
    const goalIndex = player.team;
    const goalCenterX = (goals[goalIndex].x1 + goals[goalIndex].x2)/2;
    const goalCenterY = (goals[goalIndex].y1 + goals[goalIndex].y2)/2;
    return calculateEuclideanDistance(goalCenterX, goalCenterY, player.x, player.y);
}

const getPlayerWithBall = (players) => {
    return players.find(player => player.holdsBall) || null;
}

const getTeammate = (ballHolder, players) => {
    // TODO
    return 1;
}

const getTeammates = (ballHolder, players) => {
    // TODO
    return 1;
}

const calculateDistanceBetweenPlayers = (player1, player2) => {
    return calculateEuclideanDistance(player1.x, player1.y, player2.x, player2.y)
}

const pathToGoalIsFree = (ballHolder, teammate, goals) => {
    // TODO
    return 1;
}

const goalInSightRange = (sightDirection, goals) => {
    // TODO
    return true;
}

const teammateInSightRange = (sightDirection, teammate) => {
    // TODO
    return true;
}

const sortByDistance = (teammatesDistance) => {
    // TODO
    return teammatesDistance;
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

const doNothing = (res) => {
    // TODO
    res.status(200).json({ "success": "doNothing" });
}

exports.modeController = {
    singlePlayerMode(req, res) {
        const { body } = req;

        const goalDistance = calculateDistanceToGoal(body.players[0], body.goals);
        if (goalDistance <= MIN_GOAL_PASSING_DISTANCE) {
            return recommendMovingAwayFromGoal(res, body.players[0], body.goals[0]);
        } else if (goalDistance >= MAX_GOAL_PASSING_DISTANCE) {
            return recommendMovingTowardsGoal(res, body.players[0], body.goals[0]);
        } else {
            return recommendDirectShotOnGoal(res, body.players[0], body.goals[0]);
        } 
    },
    sameTeamModeA(req, res) {
        const { body } = req;

        const ballHolder = getPlayerWithBall(body.players);
        if (!ballHolder) {
            return doNothing(res);    // No player with ball
        }

        const teammate = getTeammate(ballHolder, body.players);
        const teammateDistance = calculateDistanceBetweenPlayers(ballHolder, teammate);
        const goalDistance = calculateDistanceToGoal(ballHolder, body.goals);

        if (isBetween(goalDistance, MIN_GOAL_PASSING_DISTANCE, MAX_GOAL_PASSING_DISTANCE) &&
            pathToGoalIsFree(ballHolder, teammate, body.goals)) {
            return recommendDirectShotOnGoal(res, body.players[0], body.goals[0]);
        } else if (isBetween(teammateDistance, MIN_TEAMMATE_PASSING_DISTANCE, MAX_TEAMMATE_PASSING_DISTANCE)) {
            return recommendPassToTeammate(res, ballHolder, teammate);
        } else {
            return recommendKeepTheBall(res);
        }
    },
    sameTeamModeB(req, res) {
        const { body } = req;

        const ballHolder = getPlayerWithBall(body.players);
        if (!ballHolder) {
            return doNothing(res);    // No player with ball
        }

        const teammates = getTeammates(ballHolder, body.players);
        const teammatesDistance = calculateDistanceBetweenPlayers(ballHolder, teammates);
        const goalDistance = calculateDistanceToGoal(ballHolder, body.goals);

        if (isBetween(goalDistance, MIN_GOAL_PASSING_DISTANCE, MAX_GOAL_PASSING_DISTANCE) &&
            pathToGoalIsFree(ballHolder, teammates, body.goals) &&
            goalInSightRange(ballHolder.sightDirection, body.goals)) {
            return recommendDirectShotOnGoal(res, body.players[0], body.goals[0]);
        } else {
            sortedTeammates = sortByDistance(teammatesDistance)
            sortedTeammates.forEach(teammate => {
                if (teammateInSightRange(ballHolder.sightDirection, teammate)) {
                    return recommendPassToTeammate(res, ballHolder, teammate);
                }
            });
        }

        return recommendKeepTheBall(res);
    },
    differentTeamsModeA(req, res) {
        const { body } = req;

        res.status(200).json({ "success": "not implemented." });
    },
    differentTeamsModeB(req, res) {
        const { body } = req;

        res.status(200).json({ "success": "not implemented." });
    },
    fullGameMode(req, res) {
        const { body } = req;

        res.status(200).json({ "success": "not implemented." });
    },
}