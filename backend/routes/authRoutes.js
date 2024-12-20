import express from "express"
import bcrypt from "bcrypt";
import User from "../models/User1.js"
import jwt from "jsonwebtoken"

const router = express.Router();

router.post('/signup', async (req, res) => {
  try {
    const { email, password } = req.body;
    if (!email || !password) {
        return res.status(400).json({ message: 'Email and password are required' });
    }
    console.log('email ' + email);
    console.log('pass ' + password);

    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return res.status(400).json({ message: 'User already exists' });
    }

    const newUser = new User({ email, password });
    await newUser.save();

    res.status(201).json({ message: 'User registered successfully' });
  } catch (error) {
    console.log('')
    res.status(500).json({ message: 'Error registering user', error: error.message });
  }
});

router.post('/sigin', async (req, res) => {
    
    try {
        const {email, password} = req.body;
        const user = await User.findOne({email});
        if(!user){
            return res.status(404).json({ message: 'User not found' });
        }
        const isPasswordValid = await bcrypt.compare(password, user.password);
        if (!isPasswordValid) {
            return res.status(401).json({ message: 'Invalid credentials' });
        }
        const token = jwt.sign({ id: user._id }, process.env.JWT_SECRET, { expiresIn: '1h' });

        res.status(200).json({ message: 'Signin successful', token });
    } catch (error) {
        res.status(500).json({ message: 'Error signing in', error: error.message });
    }
})

export default router