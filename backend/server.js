
import express from 'express'
import dotenv  from 'dotenv'
import connectDB from './config/db.js'
import authRoutes from './routes/authRoutes.js'
import bodyParser from 'body-parser'
import cors from 'cors'

const app = express();
dotenv.config();
app.use(bodyParser.json());
app.use(cors());
connectDB();
//User auth Routes
app.use('/api/auth', authRoutes);

const PORT = process.env.PORT || 5111;
app.listen(PORT, () => {
  console.log('Server is listening to the port : "' +  PORT + '" ');
})


