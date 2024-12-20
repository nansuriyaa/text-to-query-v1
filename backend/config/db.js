import mongoose from 'mongoose';
const connectDB = async() => {
    try{
        await mongoose.connect(process.env.MONGO_URI);
        console.log('mongoDB connection is healthy');
    }catch(error) {
        console.log('mongoDB connection failed: "'+ error+'" ');
    }
}
export default connectDB;