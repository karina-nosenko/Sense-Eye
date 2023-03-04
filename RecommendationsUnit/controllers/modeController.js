const axios = require('axios');

IP_ADDRESS = "172.26.89.38:5000"

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

const getTeammates = (ballHolder, players) => {
    return players.filter(player => player.id != ballHolder.id);
}

const calculateDistanceBetweenPlayers = (player1, player2) => {
    return calculateEuclideanDistance(player1.x, player1.y, player2.x, player2.y)
}

const pathToGoalIsFree = (ballHolder, teammates, goals) => {
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

    return axios.get('http://' + IP_ADDRESS + '/send_recommendation_to_color?color=red&output_state=1')
    .then(function (response) {
        res.status(200).json({ "success": "recommendMovingAwayFromGoal" });
    })
    .catch(function (error) {
        res.status(200).json({ "error": "recommendMovingAwayFromGoal" });
    })
}

const recommendMovingTowardsGoal = (res, player, goal) => {
    // TODO
    return axios.get('http://' + IP_ADDRESS + '/send_recommendation_to_color?color=red&output_state=2')
    .then(function (response) {
        res.status(200).json({ "success": "recommendMovingAwayFromGoal" });
    })
    .catch(function (error) {
        res.status(200).json({ "error": "recommendMovingAwayFromGoal" });
    })
}

const recommendDirectShotOnGoal = (res, player, goal) => {
    // TODO
    return axios.get('http://' + IP_ADDRESS + '/send_recommendation_to_color?color=red&output_state=3')
    .then(function (response) {
        res.status(200).json({ "success": "recommendMovingAwayFromGoal" });
    })
    .catch(function (error) {
        res.status(200).json({ "error": "recommendMovingAwayFromGoal" });
    })
}

const recommendPassToTeammate = (res, ballHolder, teammate) => {
    // TODO
    return axios.get('http://' + IP_ADDRESS + '/send_recommendation_to_color?color=red&output_state=4')
    .then(function (response) {
        res.status(200).json({ "success": "recommendMovingAwayFromGoal" });
    })
    .catch(function (error) {
        res.status(200).json({ "error": "recommendMovingAwayFromGoal" });
    })
}

const recommendKeepTheBall = (res) => {
    // TODO
    return axios.get('http://' + IP_ADDRESS + '/send_recommendation_to_color?color=red&output_state=5')
    .then(function (response) {
        res.status(200).json({ "success": "recommendMovingAwayFromGoal" });
    })
    .catch(function (error) {
        res.status(200).json({ "error": "recommendMovingAwayFromGoal" });
    })
}

const doNothing = (res) => {
    // TODO
    return axios.get('http://' + IP_ADDRESS + '/send_recommendation_to_color?color=red&output_state=6')
    .then(function (response) {
        res.status(200).json({ "success": "recommendMovingAwayFromGoal" });
    })
    .catch(function (error) {
        res.status(200).json({ "error": "recommendMovingAwayFromGoal" });
    })
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

        const teammates = getTeammates(ballHolder, body.players);   
        const teammateDistance = calculateDistanceBetweenPlayers(ballHolder, teammates[0]);
        const goalDistance = calculateDistanceToGoal(ballHolder, body.goals);

        if (isBetween(goalDistance, MIN_GOAL_PASSING_DISTANCE, MAX_GOAL_PASSING_DISTANCE) &&
            pathToGoalIsFree(ballHolder, teammates, body.goals)) {
            return recommendDirectShotOnGoal(res, body.players[0], body.goals[0]);
        } else if (isBetween(teammateDistance, MIN_TEAMMATE_PASSING_DISTANCE, MAX_TEAMMATE_PASSING_DISTANCE)) {
            return recommendPassToTeammate(res, ballHolder, teammates[0]);
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