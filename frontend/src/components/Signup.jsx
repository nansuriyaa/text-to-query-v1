import * as React from 'react';
import { Form, Field, FormElement, FieldWrapper } from '@progress/kendo-react-form';
import { Error } from '@progress/kendo-react-labels';
import { Input } from '@progress/kendo-react-inputs';
import { Button } from '@progress/kendo-react-buttons';
import axios from 'axios'
import { useNavigate } from 'react-router-dom';
const emailRegex = new RegExp(/\S+@\S+\.\S+/);
const emailValidator = value => emailRegex.test(value) ? '' : 'Please enter a valid email.';
const EmailInput = fieldRenderProps => {
  const {
    validationMessage,
    visited,
    ...others
  } = fieldRenderProps;
  return <div className="k-form-field-wrap">
            <Input {...others} labelClassName={'k-form-label'} />
            {visited && validationMessage && <Error>{validationMessage}</Error>}
        </div>;
};
const Signup = () => {
  
  const navigate = useNavigate();
  
  const handleSubmit = async (dataItem) => {
  
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

  return <Form onSubmit={handleSubmit} render={formRenderProps => <FormElement style={{
    maxWidth: 650
  }}>
                    <fieldset className={'k-form-fieldset'}>
                        <legend className={'k-form-legend'}>Please fill in the fields:</legend>

                        <FieldWrapper>
                            <Field name={'email'} type={'email'} component={EmailInput} label={'Email'} validator={emailValidator} />
                        </FieldWrapper>
                    </fieldset>
                    <div className="k-form-buttons">
                        
                        <FieldWrapper>
                            <div className="k-form-field-wrap">
                                <Field name={'password'} component={Input} labelClassName={'k-form-label'} label={'Password'} />
                            </div>
                        </FieldWrapper> 

                        <Button disabled={!formRenderProps.allowSubmit}>Submit</Button>
                    </div>
                </FormElement>} />;
};
export default Signup;
