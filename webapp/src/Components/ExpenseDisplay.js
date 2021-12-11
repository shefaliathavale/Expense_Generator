
import React, { useState, useRef } from "react";
import AuthService from "../services/auth.service";

const Profile = () => {
  const currentUser = AuthService.getCurrentUser();
  console.log(currentUser.username)

  var dateObj = new Date();
var currmonth = dateObj.getUTCMonth() + 1; //months from 1-12
//var day = dateObj.getUTCDate();
//var year = dateObj.getUTCFullYear();
var newdate = ''
newdate = "/ M :" + currmonth ;

const [month, setMonth] = useState(currmonth);
const [category, setCategory] = useState("Miscellaneous");
const [message, setMessage] = useState("");

const onFormSubmit = (e) => {

  setMessage("");

  e.preventDefault() // Stop form submit
  console.log(month)
  AuthService.getexpenses(currentUser.username,month, category).then((response)=>{
    console.log(response)
    setMessage(response);
  },
  (error) => {
    const resMessage =
      (error.response &&
        error.response.data &&
        error.response.data.message) ||
      error.message ||
      error.toString();

  }
  )
}

const onMonthChange =(e) => {
  console.log(e.target.value)     
  const month = e.target.value;
  setMonth(month);
};


const onCategoryChange =(e) =>{
  console.log(e.target.value)     
  const category = e.target.value;
  setCategory(category);
};

  return (

    <form onSubmit={onFormSubmit}>
        <h1> Expenses </h1>
<div> 
       
      <strong>Selected Month :</strong> {month}
</div>
        <div>
              <select value={month} onChange={onMonthChange} required> 
                <option value="DEFAULT" >Choose category</option>
                <option name="January" value="1"> Jan</option>
                  <option name="February" value="2"> Feb</option>
                  <option name="March" value="3">March</option>
                  <option name="April" value="4"> April</option>
                  <option name="May" value="5"> May</option>
                  <option name="June" value="6"> June</option>
                  <option name="July" value="7"> July </option>
                  <option name="August" value="8"> August </option>
                  <option name="September" value="9"> September </option>
                  <option name="October" value="10"> October</option>
                  <option name="November" value="11"> November</option>
                  <option name="December" value="12"> December</option>
              </select>
       

              <select value={category} onChange={onCategoryChange}  required> 
                <option value="DEFAULT" disabled>Choose category</option>
                <option name="Miscellaneous" value="Miscellaneous"> Miscellaneous</option>
                  <option name="Grocery"> Grocery</option>
                  <option name="Shopping">Shopping</option>
                  <option name="Rent"> Rent</option>
                  <option name="School"> School</option>
                  <option name="Transportation"> Transportation</option>
                  <option name="Medical"> Medical </option>
                  <option name="Food"> Food </option>
                  <option name="Vacation"> Vacation </option>
                  <option name="House Maintenance"> Maintenance</option>
              </select>

      <span> </span> <span> </span> 
        <button type="submit"> Get Expenses </button>
        </div>
        
        {message? (
          <div>
              {message!== "" ? ( <p> Total Expense according to category and month is:  {message}</p> ) : <p> Total Expense according to category and month is: - </p> }

              </div>
          ) : null }


      </form>

  


  );
};

export default Profile;