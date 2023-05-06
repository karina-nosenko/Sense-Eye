const axios = require('axios');
const fs = require('fs');

HARDWARE_API_ADDRESS = "172.26.87.255:5000"

const { MAX_GOAL_PASSING_DISTANCE,
    MIN_GOAL_PASSING_DISTANCE,
    MAX_TEAMMATE_PASSING_DISTANCE,
    MIN_TEAMMATE_PASSING_DISTANCE,
    MAX_OPPONENT_DISTANCE } = require('../constants');

const getColorNameById = (id) => {
    switch (id) {
        case 0:
            return 'yellow';
        case 1:
            return 'orange';
        case 2:
            return 'blue';
        default:
            return 'undefined';
    }
}

const isBetween = (thing, min, max) => {
    return (thing >= min) && (thing <= max);
}

const calculateEuclideanDistance = (x1, y1, x2, y2) => {
    return Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
}

const getClockDirection = (player, pointX, pointY) => { // clock direction 
    const playerDirection = player.sightDirection;

    // Calculate the angle from the player to the point
    const deltaX = pointX - player.x;
    const deltaY = player.y - pointY;
    let directionDegrees = (Math.atan2(deltaY, deltaX) * 180 / Math.PI + 360) % 360;
    directionDegrees = directionDegrees < 0 ? 360 + directionDegrees : directionDegrees;

    // Calculate the angle difference between the point direction and the player direction
    let angleDiff = playerDirection - directionDegrees;
    if (angleDiff < 0) {
        angleDiff += 360;
    }

    // Calculate the clock number
    let clockNumber = Math.ceil(angleDiff / 30) % 12;
    if (clockNumber === 0) {
        clockNumber = 12;
    }

    return clockNumber;
}

const getClockDirectionToGoal = (player, goal) => {
    const clockToLeftGoalSide = getClockDirection(player, goal.x1, goal.y1);
    const clockToRightGoalSide = getClockDirection(player, goal.x2, goal.y2);

    let middleClock = Math.round((clockToLeftGoalSide + clockToRightGoalSide) / 2) % 12 || 12;
    if (Math.abs(clockToLeftGoalSide - middleClock) > 5) {
        return clockToLeftGoalSide;
    } else if (Math.abs(clockToRightGoalSide - middleClock) > 5) {
        return clockToRightGoalSide;
    } else {
        return middleClock;
    }
}

const calculateDistanceToGoal = (player, goals) => {
    const goalIndex = player.team;
    const goalCenterX = (goals[goalIndex].x1 + goals[goalIndex].x2) / 2;
    const goalCenterY = (goals[goalIndex].y1 + goals[goalIndex].y2) / 2;
    return calculateEuclideanDistance(goalCenterX, goalCenterY, player.x, player.y);
}

//TODO return true if the ball_holder is close to goal
const is_close_to_goal = (player, goals) => {
    const goalIndex = player.team;
    const goalCenterX = (goals[goalIndex].x1 + goals[goalIndex].x2) / 2;
    const goalCenterY = (goals[goalIndex].y1 + goals[goalIndex].y2) / 2;
    const wrongGoalCenterX = (goals[!goalIndex].x1 + goals[!goalIndex].x2) / 2;
    const wrongGoalWrongCenterY = (goals[!goalIndex].y1 + goals[!goalIndex].y2) / 2;
    const distance_player_from_goal = calculateEuclideanDistance(goalCenterX, goalCenterY, player.x, player.y);
    const distance_player_from_wrong_goal = calculateEuclideanDistance(wrongGoalCenterX, wrongGoalWrongCenterY, player.x, player.y);
    if (distance_player_from_goal < distance_player_from_wrong_goal)
        return true;
    else return false;
}

const isPlayerInsideTriangle = (player, point1, point2, point3) => {
    // Calculate the areas of the main triangle and three sub-triangles
    const mainTriangleArea = Math.abs(
        (point2.x - point1.x) * (point3.y - point1.y) -
        (point3.x - point1.x) * (point2.y - point1.y)
    );
    const subTriangle1Area = Math.abs(
        (player.x - point1.x) * (point2.y - point1.y) -
        (point2.x - point1.x) * (player.y - point1.y)
    );
    const subTriangle2Area = Math.abs(
        (player.x - point2.x) * (point3.y - point2.y) -
        (point3.x - point2.x) * (player.y - point2.y)
    );
    const subTriangle3Area = Math.abs(
        (player.x - point3.x) * (point1.y - point3.y) -
        (point1.x - point3.x) * (player.y - point3.y)
    );

    // Check whether the sum of sub-triangle areas equals the main triangle area
    return (
        subTriangle1Area + subTriangle2Area + subTriangle3Area <= mainTriangleArea
    );
};

const getPlayerWithBall = (players) => {
    return players.find(player => player.holdsBall) || null;
}
const getPlayerOpponent = (players, opponent_team_index) => {
    return players.find(player => (player.team == opponent_team_index));
}
const getTeammates = (ballHolder, players) => {
    return players.filter(player => (player.id != ballHolder.id) && (player.team == ballHolder.team));
}

// const calculateDistanceBetweenPlayers = (player1, player2) => {
//     return calculateEuclideanDistance(player1.x, player1.y, player2.x, player2.y)
// }


//YUVAL
const calculateDistanceBetweenPlayers = (player1, ...points) => {
    let distances = [];
    for (let i = 0; i < points.length; i += 2) {
        let x2 = points[i];
        let y2 = points[i + 1];
        distances.push(calculateEuclideanDistance(player1.x1, player1.y1, x2, y2));
    }
    return distances;
};

const pathToGoalIsFree = (ballHolder, teammates, goal) => {
    const point1 = { x: goal.x1, y: goal.y1 };
    const point2 = { x: goal.x2, y: goal.y2 };
    const point3 = { x: ballHolder.x, y: ballHolder.y };

    return !teammates.some(teammate => {
        return isPlayerInsideTriangle(teammate, point1, point2, point3);
    });
}

const goalInSightRange = (ballHolder, goal) => {
    const output_state = getClockDirectionToGoal(ballHolder, goal)
    return [9, 10, 11, 12, 1, 2, 3].includes(output_state);
}

const playerInSightRange = (ballHolder, player) => {
    const output_state = getClockDirection(ballHolder, player.x, player.y)
    return [9, 10, 11, 12, 1, 2, 3].includes(output_state);
}


// const sortedTeammates = (teammatesDistance) => {
//     let distances = [];
//     for (let i = 0; i < teammatesDistance.length; i++) {
//         distances.push({ index: i, distance: teammatesDistance[i] });
//     }
//     distances.sort((a, b) => a.distance - b.distance);
//     let sortedTeammates = [];
//     for (let i = 0; i < distances.length; i++) {
//         sortedTeammates.push([teammates[(distances[i].index * 2)], teammates[(distances[i].index * 2) + 1]]);
//     }
//     return sortedTeammates;
// };


const sortByDistance = (teammatesDistance) => {
    // TODO
    return teammatesDistance;
}

//YUVAL
const sortPlayersByDistance = (players, playersDistance) => {
    // Combine each player with their corresponding distance as a tuple
    const tuples = players.map((player, i) => [player, playersDistance[i]]);

    // Sort the tuples based on the distance (second element in each tuple)
    tuples.sort((a, b) => a[1] - b[1]);

    // Extract only the sorted players (first element in each tuple)
    return tuples.map(tuple => tuple[0]);
};


const recommendMovingAwayFromGoal = (res, ballHolder, goal) => {
    let output_state = getClockDirectionToGoal(ballHolder, goal)

    // Calculate the opposite direction
    if (output_state > 6) {
        output_state -= 6;
    } else {
        output_state += 6;
    }

    const color = getColorNameById(ballHolder.id);

    return res.status(200).json({ 'color': color, 'output_state': output_state, 'state': 'move' });
    // return axios.get(`http://${HARDWARE_API_ADDRESS}/recommend?color=${color}&output_state=${output_state}&state=move`)
    //     .then(function (response) {
    //         res.status(200).json({ 'color': color, 'output_state': output_state, 'state': 'move' });
    //     })
    //     .catch(function (error) {
    //         res.status(200).json({ 'color': '', 'output_state': '', 'state': '' });
    //     })
}

const recommendMovingAwayFromOpponent = (res, ballHolder, opponent) => { //TODO yuval
    let output_state = getClockDirection(ballHolder, opponent.x, opponent.y);
    const color = getColorNameById(ballHolder.id);

    if (output_state <= 6)
        output_state += 6;
    else
        output_state -= 6;

    return res.status(200).json({ 'color': color, 'output_state': output_state, 'state': 'move' });
    // return axios.get(`http://${HARDWARE_API_ADDRESS}/recommend?color=${color}&output_state=${output_state}&state=move`)
    //     .then(function (response) {
    //         res.status(200).json({ 'color': color, 'output_state': output_state, 'state': 'move' });
    //     })
    //     .catch(function (error) {
    //         res.status(200).json({ 'color': '', 'output_state': '', 'state': '' });
    //     })
}

const recommendMovingTowardsGoal = (res, ballHolder, goal) => {
    let output_state = getClockDirectionToGoal(ballHolder, goal)

    const color = getColorNameById(ballHolder.id);

    return res.status(200).json({ 'color': color, 'output_state': output_state, 'state': 'move' });
    // return axios.get(`http://${HARDWARE_API_ADDRESS}/recommend?color=${color}&output_state=${output_state}&state=move`)
    //     .then(function (response) {
    //         res.status(200).json({ 'color': color, 'output_state': output_state, 'state': 'move' });
    //     })
    //     .catch(function (error) {
    //         res.status(200).json({ 'color': '', 'output_state': '', 'state': '' });
    //     })
}

const recommendDirectShotOnGoal = (res, ballHolder, goal) => {
    let output_state = getClockDirectionToGoal(ballHolder, goal)

    const color = getColorNameById(ballHolder.id);
    // return axios.get(`http://${HARDWARE_API_ADDRESS}/recommend?color=${color}&output_state=${output_state}&state=kick`)
    //     .then(function (response) {
    //         res.status(200).json({'color': color,'output_state':output_state,'state':'kick'});
    //     })
    //     .catch(function (error) {
    //         res.status(200).json({'color': '','output_state':'','state':''});
    //     })
    return res.status(200).json({ 'color': color, 'output_state': output_state, 'state': 'kick' });
}

const recommendPassToTeammate = (res, ballHolder, teammate) => {
    console.log("recommendPassToTeammate");
    let output_state = getClockDirection(ballHolder, teammate.x, teammate.y)

    const color = getColorNameById(ballHolder.id);
    // return axios.get(`http://${HARDWARE_API_ADDRESS}/recommend?color=${color}&output_state=${output_state}&state=pass`)
    //     .then(function (response) {
    //         res.status(200).json({'color': color,'output_state':output_state,'state':'pass'});
    //     })
    //     .catch(function (error) {
    //         res.status(200).json({'color': '','output_state':'','state':''});
    //     })
    return res.status(200).json({ 'color': color, 'output_state': output_state, 'state': 'pass' });
}

const recommendKeepTheBall = (res, ballHolder) => {
    console.log("recommendKeepTheBall");
    const color = getColorNameById(ballHolder.id);
    return res.status(200).json({ 'color': color, 'output_state': 0, 'state': 'move' });
    // return axios.get(`http://${HARDWARE_API_ADDRESS}/recommend?color=${color}&output_state=${0}&state=move`)
    //     .then(function (response) {
    //         res.status(200).json({ 'color': color, 'output_state': 0, 'state': 'move' });
    //     })
    //     .catch(function (error) {
    //         res.status(200).json({ 'color': '', 'output_state': '', 'state': '' });
    //     })
    // return res.status(200).json({ 'color': color, 'output_state': 0, 'state': 'move' });
}

const doNothing = (res) => {
    res.status(200).json({ "doNothing": "No player with the ball was found." });
}

exports.modeController = {
    singlePlayerMode(req, res) {
        const { body } = req;

        const goalDistance = calculateDistanceToGoal(body.players[0], body.goals);
        const goalIndex = body.players[0].team;
        if (goalDistance <= MIN_GOAL_PASSING_DISTANCE) {
            return recommendMovingAwayFromGoal(res, body.players[0], body.goals[goalIndex]);
        } else if (goalDistance >= MAX_GOAL_PASSING_DISTANCE) {
            return recommendMovingTowardsGoal(res, body.players[0], body.goals[goalIndex]);
        } else {
            return recommendDirectShotOnGoal(res, body.players[0], body.goals[goalIndex]);
        }
    },
    sameTeamModeA(req, res) {
        const { body } = req;

        const ballHolder = getPlayerWithBall(body.players);
        if (!ballHolder) {
            return doNothing(res);    // No player with ball
        }

        const teammates = getTeammates(ballHolder, body.players);
        const teammateDistance = calculateEuclideanDistance(ballHolder.x, ballHolder.y, teammates[0].x, teammates[0].y);
        const goalDistance = calculateDistanceToGoal(ballHolder, body.goals);
        const goalIndex = ballHolder.team;

        if (isBetween(goalDistance, MIN_GOAL_PASSING_DISTANCE, MAX_GOAL_PASSING_DISTANCE) &&
            pathToGoalIsFree(ballHolder, teammates, body.goals[goalIndex])) {
            return recommendDirectShotOnGoal(res, ballHolder, body.goals[goalIndex]);
        } else if (isBetween(teammateDistance, MIN_TEAMMATE_PASSING_DISTANCE, MAX_TEAMMATE_PASSING_DISTANCE)) {
            return recommendPassToTeammate(res, ballHolder, teammates[0]);
        } else {
            return recommendKeepTheBall(res, ballHolder);
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
        const goalIndex = ballHolder.team;

        if (isBetween(goalDistance, MIN_GOAL_PASSING_DISTANCE, MAX_GOAL_PASSING_DISTANCE) &&
            pathToGoalIsFree(ballHolder, teammates, body.goals[goalIndex]) &&
            goalInSightRange(ballHolder, body.goals[goalIndex])) {
            return recommendDirectShotOnGoal(res, ballHolder, body.goals[goalIndex]);
        } else {
            sortedTeammates = sortByDistance(teammatesDistance) // TODO - fix calculateDistanceBetweenPlayers
            sortedTeammates.forEach(teammate => {
                if (playerInSightRange(ballHolder, teammate)) {
                    return recommendPassToTeammate(res, ballHolder, teammate);
                }
            });
        }

        return recommendKeepTheBall(res);
    },
    differentTeamsModeA(req, res) {
        const { body } = req;

        const ballHolder = getPlayerWithBall(body.players);
        if (!ballHolder) {
            return doNothing(res);    // No player with ball
        }

        const goalIndex = ballHolder.team;
        const teammates = getTeammates(ballHolder, body.players);
        let opponent_team_index = ballHolder.team
        let opponent = getPlayerOpponent(body.players, opponent_team_index);
        let opponentDistance = calculateEuclideanDistance(ballHolder, opponent);
        let goalDistance = calculateDistanceToGoal(ballHolder, body.goals);

        if (opponent_team_index == 0)
            opponent_team_index = 1;
        else opponent_team_index = 0;
        if (isBetween(goalDistance, MIN_GOAL_PASSING_DISTANCE, MAX_GOAL_PASSING_DISTANCE) &&
            goalInSightRange(ballHolder, body.goals[goalIndex])
            &&
            pathToGoalIsFree(ballHolder, teammates, body.goals[goalIndex]))
            return recommendDirectShotOnGoal(res, ballHolder, body.goals[goalIndex]);
        else if (opponentDistance <= MAX_OPPONENT_DISTANCE &&
            playerInSightRange(ballHolder, opponent))
            return recommendMovingAwayFromOpponent(res, ballHolder, opponent);
        else
            return recommendKeepTheBall(res, ballHolder);
    },
    differentTeamsModeB(req, res) {
        const { body } = req;
        ballHolder = getPlayerWithBall(body.players);
        const goalIndex = ballHolder.team;
        teammates = getTeammates(ballHolder, body.players);
        console.log(teammates);
        teammatesDistance = calculateDistanceBetweenPlayers(ballHolder, teammates);
        opponent = getPlayerOpponent(body.players, !ballHolder.team);
        goalDistance = calculateDistanceToGoal(ballHolder, body.goals);
        if (isBetween(goalDistance, MIN_GOAL_PASSING_DISTANCE,
            MAX_GOAL_PASSING_DISTANCE)
            && pathToGoalIsFree(ballHolder, teammates, body.goals[goalIndex]))
            return recommendDirectShotOnGoal(res, ballHolder, goal);
        sortedTeammates = sortPlayersByDistance(teammates, teammatesDistance);
        for (teammate in sortedTeammates) {
            teammateToOpponentDistance = calculateEuclideanDistance(teammate, opponent);
            teammateToBallHolderDistance = calculateEuclideanDistance(teammate, ballHolder);
            if (playerInSightRange(ballHolder, teammate)
                && teammateToOpponentDistance > teammateToBallHolderDistance)
                return recommendPassToTeammate(res, ballholder, teammate);
        }
        return recommendKeepTheBall(res, ballHolder);
        // res.status(200).json({ "differentTeamsModeB": "not implemented." });
    },
    fullGameMode(req, res) {
        const { body } = req;

        res.status(200).json({ "fullGameMode": "not implemented." });
    },
}