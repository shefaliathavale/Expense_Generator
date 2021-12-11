import React, { useState, useEffect } from "react";
import { Link } from 'react-router-dom';
//import UserService from "../services/user.service";
import AuthService from "../services/auth.service";
const Home = () => {
  const [content, setContent] = useState("");
  const currentUser = AuthService.getCurrentUser();
console.log(currentUser)

  // useEffect(() => {
  //   UserService.getPublicContent().then(
  //     (response) => {
  //       setContent(response.data);
  //     },
  //     (error) => {
  //       const _content =
  //         (error.response && error.response.data) ||
  //         error.message ||
  //         error.toString();

  //       setContent(_content);
  //     }
  //   );
  // }, []);

  return (
    <div className="container">
      <header className="jumbotron">
        <h3>Welcome to Expense Generator</h3>

        <h6>  Hi {currentUser.username}</h6>
    <div>
        <p>To view list of expenses based on months and category: </p>
          
              <Link to="/expensedisplay"> Expense list </Link>
    </div> 
      </header>
    </div>
  );
};

export default Home;