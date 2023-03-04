const axios = require('axios');

HARDWARE_API_ADDRESS = "172.26.89.38:5000"

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

const getClockDirection = (player, pointX, pointY) => {
    // Calculate the angle between the player and the point
    const deltaX = pointX - player.x;
    const deltaY = player.y - pointY;   // inverted y-axis
    const directionDegrees = (Math.atan2(deltaY, deltaX) * 180 / Math.PI + 360) % 360;

    // Calculate the angle difference between the point direction and the player direction
    let angleDiff = directionDegrees - player.sightDirection;
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
    // console.log(player)
    // console.log(goal)
    // console.log(clockToLeftGoalSide)
    // console.log(clockToRightGoalSide)

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
    const goalCenterX = (goals[goalIndex].x1 + goals[goalIndex].x2)/2;
    const goalCenterY = (goals[goalIndex].y1 + goals[goalIndex].y2)/2;
    return calculateEuclideanDistance(goalCenterX, goalCenterY, player.x, player.y);
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

const getTeammates = (ballHolder, players) => {
    return players.filter(player => (player.id != ballHolder.id) && (player.team == ballHolder.team));
}

const calculateDistanceBetweenPlayers = (player1, player2) => {
    return calculateEuclideanDistance(player1.x, player1.y, player2.x, player2.y)
}

const pathToGoalIsFree = (ballHolder, teammates, goal) => {
    const point1 = {x: goal.x1, y: goal.y1};
    const point2 = {x: goal.x2, y: goal.y2};
    const point3 = {x: ballHolder.x, y: ballHolder.y};

    return !teammates.some(teammate => {
        return isPlayerInsideTriangle(teammate, point1, point2, point3);
    });
}

const goalInSightRange = (ballHolder, goal) => {
    const output_state = getClockDirectionToGoal(ballHolder, goal)  
    return [9, 10, 11, 12, 1, 2, 3].includes(output_state);
}

const teammateInSightRange = (ballHolder, teammate) => {
    const output_state = getClockDirection(ballHolder, teammate.x, teammate.y)  
    return [9, 10, 11, 12, 1, 2, 3].includes(output_state);
}

const sortByDistance = (teammatesDistance) => {
    // TODO
    return teammatesDistance;
}

const recommendMovingAwayFromGoal = (res, ballHolder, goal) => {
    let output_state = getClockDirectionToGoal(ballHolder, goal)

    // Calculate the opposite direction
    if (output_state > 6) {
        output_state -= 6;
    } else {
        output_state += 6;
    }

    res.status(200).json({ "recommendMovingAwayFromGoal": `color:${ getColorNameById(ballHolder.id) }, output_state:${ output_state }` });
    // return axios.get('http://' + HARDWARE_API_ADDRESS + '/send_recommendation_to_color?color=red&output_state=6')
    // .then(function (response) {
    //     res.status(200).json({ "success": "recommendMovingAwayFromGoal" });
    // })
    // .catch(function (error) {
    //     res.status(200).json({ "error": "recommendMovingAwayFromGoal" });
    // })
}

const recommendMovingTowardsGoal = (res, ballHolder, goal) => {
    let output_state = getClockDirectionToGoal(ballHolder, goal)

    res.status(200).json({ "recommendMovingTowardsGoal": `color:${ getColorNameById(ballHolder.id) }, output_state:${ output_state }` });
    // return axios.get('http://' + HARDWARE_API_ADDRESS + '/send_recommendation_to_color?color=red&output_state=6')
    // .then(function (response) {
    //     res.status(200).json({ "success": "recommendMovingAwayFromGoal" });
    // })
    // .catch(function (error) {
    //     res.status(200).json({ "error": "recommendMovingAwayFromGoal" });
    // })
}

const recommendDirectShotOnGoal = (res, ballHolder, goal) => {
    let output_state = getClockDirectionToGoal(ballHolder, goal)

    res.status(200).json({ "recommendDirectShotOnGoal": `color:${ getColorNameById(ballHolder.id) }, output_state:${ output_state }` });
    // return axios.get('http://' + HARDWARE_API_ADDRESS + '/send_recommendation_to_color?color=red&output_state=6')
    // .then(function (response) {
    //     res.status(200).json({ "success": "recommendMovingAwayFromGoal" });
    // })
    // .catch(function (error) {
    //     res.status(200).json({ "error": "recommendMovingAwayFromGoal" });
    // })
}

const recommendPassToTeammate = (res, ballHolder, teammate) => {
    let output_state = getClockDirection(ballHolder, teammate.x, teammate.y)

    res.status(200).json({ "recommendPassToTeammate": `color:${ getColorNameById(ballHolder.id) }, output_state:${ output_state }` });
    // return axios.get('http://' + HARDWARE_API_ADDRESS + '/send_recommendation_to_color?color=red&output_state=6')
    // .then(function (response) {
    //     res.status(200).json({ "success": "recommendMovingAwayFromGoal" });
    // })
    // .catch(function (error) {
    //     res.status(200).json({ "error": "recommendMovingAwayFromGoal" });
    // })
}

const recommendKeepTheBall = (res, ballHolder) => {

    res.status(200).json({ "recommendKeepTheBall": `color:${ getColorNameById(ballHolder.id) }, output_state:${ 0 }` });

    // return axios.get('http://' + HARDWARE_API_ADDRESS + '/send_recommendation_to_color?color=red&output_state=6')
    // .then(function (response) {
    //     res.status(200).json({ "success": "recommendMovingAwayFromGoal" });
    // })
    // .catch(function (error) {
    //     res.status(200).json({ "error": "recommendMovingAwayFromGoal" });
    // })
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
        const teammateDistance = calculateDistanceBetweenPlayers(ballHolder, teammates[0]);
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
            return recommendDirectShotOnGoal(res, body.players[0], body.goals[goalIndex]);
        } else {
            sortedTeammates = sortByDistance(teammatesDistance) // TODO - fix calculateDistanceBetweenPlayers
            sortedTeammates.forEach(teammate => {
                if (teammateInSightRange(ballHolder, teammate)) {
                    return recommendPassToTeammate(res, ballHolder, teammate);
                }
            });
        }

        return recommendKeepTheBall(res);
    },
    differentTeamsModeA(req, res) {
        const { body } = req;

        res.status(200).json({ "differentTeamsModeA": "not implemented." });
    },
    differentTeamsModeB(req, res) {
        const { body } = req;

        res.status(200).json({ "differentTeamsModeB": "not implemented." });
    },
    fullGameMode(req, res) {
        const { body } = req;

        res.status(200).json({ "fullGameMode": "not implemented." });
    },
}