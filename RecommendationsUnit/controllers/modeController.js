exports.modeController = {
    singlePlayerMode(req, res) {
        const { body } = req;

        res.status(200).json({ "success": "success" });

        // const newUser = new User(body);

        // newUser.save().then(result => {
        //     if (result) {
        //         res.status(200).json({ "success": "User added successfully" });
        //     } else {
        //         res.status(500).json({ "error": "Error adding a user" });
        //     }
        // });
    },
    sameTeamModeA(req, res) {
        const { body } = req;

        res.status(200).json({ "success": "success" });
        // User.findOne({ email: req.params.userEmail })
        //     .then(result => {
        //         res.status(200).json(result);
        //     })
        //     .catch(err => res.status(500).json({ 'error': 'error while getting user' }));
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