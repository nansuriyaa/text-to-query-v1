// const handleSubmit = async (dataItem) => {
//     try {

//       const response = await fetch('http://localhost:5111/api/signup', {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//         },
//         body: JSON.stringify(dataItem),
//       });
  
//       let result;
//       try {
//         result = await response.json();  
//       } catch (e) {
//         console.error("Error parsing JSON", e);
//       }
  
//       if (response.ok) {
//         alert('Signup successful!');
//       } else {
//         alert(`Signup failed: ${result.message || 'Unknown error'}`);
//       }
//     } catch (error) {
//       alert('Error occurred while submitting data');
//       console.error(error); // Log the error for debugging
//     }
//   };

import axios from 'axios'
import { useNavigate } from 'react-router-dom';

const handleSubmit = async (dataItem) => {
    const navigate = useNavigate();

    axios.post('http://localhost:5111/api/auth/signup', {
      email: dataItem.email,
      password: dataItem.password
    })
    .then(function (response) {
      console.log(response);
      navigate('/home');
    })
    .catch(function (error) {
      console.log(error);
    });
  }
export default handleSubmit