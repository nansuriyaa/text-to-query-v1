import React from "react";
import { Form, Field, FormElement } from "@progress/kendo-react-form";
import { Input } from "@progress/kendo-react-inputs";
import { Error } from "@progress/kendo-react-labels";

// Email validation
const emailRegex = new RegExp(/\S+@\S+\.\S+/);
const emailValidator = (value) =>
  emailRegex.test(value) ? "" : "Please enter a valid email.";

// Password validation
const passwordValidator = (value) =>
  value ? "" : "Password is required.";

// Custom Input Component for Showing Errors
const CustomInput = (fieldRenderProps) => {
  const { validationMessage, visited, ...others } = fieldRenderProps;
  return (
    <div>
      <Input {...others} />
      {visited && validationMessage && <Error>{validationMessage}</Error>}
    </div>
  );
};

// SignIn Component
const Signin = () => {
  const handleSubmit = (dataItem) => {
    console.log("Sign-In Data:", dataItem);
    alert("Sign-In Successful!");
  };

  return (
    <div style={{ maxWidth: 400, margin: "0 auto", padding: "20px" }}>
      <h2>Sign In</h2>
      <Form
        onSubmit={handleSubmit}
        render={(formRenderProps) => (
          <FormElement>
            <fieldset className="k-form-fieldset">
              <legend className="k-form-legend">Enter your credentials:</legend>
              <div className="mb-3">
                <Field
                  name="email"
                  type="email"
                  component={CustomInput}
                  label="Email"
                  validator={emailValidator}
                />
              </div>
              <div className="mb-3">
                <Field
                  name="password"
                  type="password"
                  component={CustomInput}
                  label="Password"
                  validator={passwordValidator}
                />
              </div>
            </fieldset>
            <div className="k-form-buttons">
              <button
                type="submit"
                className="k-button k-button-md k-rounded-md k-button-solid k-button-solid-primary"
                disabled={!formRenderProps.allowSubmit}
              >
                Sign In
              </button>
            </div>
          </FormElement>
        )}
      />
    </div>
  );
};

export default Signin;
