import axios from "axios";

const API_URL = "http://localhost:5000/api/auth/";

const register = (username, email, password) => {
  return axios.post(API_URL + "signup", {
    username,
    email,
    password,
  });
};


const login = (username, password) => {
  return axios
    .post(API_URL + "signin", {
      username,
      password,
    })
    .then((response) => {
      const users = response.data
      console.log(response.data)
      if (response.data.accessToken) {
        localStorage.setItem("user", JSON.stringify(users));
        console.log('users', users)
      }

      return response.data;
    });
};

const getexpenses = (username, month, category) => {
  return axios
    .post(API_URL + "getexpenses", {
      username,
      month,
      category
    })
    .then((response) => {
      const pdflist = response.data
      console.log(response.data)
      // if (response.data.accessToken) {
      //   localStorage.setItem("user", JSON.stringify(users));
      //   console.log('users', users)
      // }

      return response.data;
    });
};


const logout = () => {
  localStorage.removeItem("user");
};

const getCurrentUser = () => {
  return JSON.parse(localStorage.getItem("user"));
};

export default {
  register,
  login,
  logout,
  getCurrentUser,
  getexpenses
};