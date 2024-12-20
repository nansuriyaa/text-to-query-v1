import mongoose from "mongoose";
import bcrypt from "bcrypt";
const { Schema } = mongoose;

const userSchema = new Schema({
    email: { type: String, required: true },
    password: {type: String, required: true }
});

userSchema.pre('save', async function (next) {
    const self = this; 
    //console.log(user);
    if (self.isModified('password')) {
        self.password = await bcrypt.hash(self.password, 10);
    }

    next();
})

const User = mongoose.model('User', userSchema);

export default User



