import React from 'react'
import axios, { post } from 'axios';
import AuthService from "../services/auth.service";

const currentUser = AuthService.getCurrentUser();
console.log(currentUser)
class FileUpload extends React.Component {

  constructor(props) {
    super(props);
    this.state ={
      file:null,
      category: null,
      username:null,
      currency:null,
  data: {
    bill_value: '',
    total_value: '',
    category: ''
  },
setData:false
    }
    this.onFormSubmit = this.onFormSubmit.bind(this)
    this.onChange = this.onChange.bind(this)
    this.fileUpload = this.fileUpload.bind(this)
    this.onCurrencyChange = this.onCategoryChange.bind(this);
    this.onCategoryChange = this.onCategoryChange.bind(this);
    this.showResponseData = this.showResponseData.bind(this);
  }

  onFormSubmit(e){
    e.preventDefault() // Stop form submit
    this.fileUpload(this.state.file).then((response)=>{
      alert("Upload Successful")
      e.target.reset();
      console.log(response.data)
      this.setState({data : response.data})
     // window.location = '/profile';
     this.showResponseData(response.data)
      //return response.data;
    })
  }

  showResponseData(data){ 
  this.setState({
    setData: !this.state.setData
    });
  }

  
  onChange(e) {
   // console.log(e.target.files[0].name)
          if(e.target.files[0])
          {

            var filePath = e.target.files[0].name;
            // Allowing file type
            var allowedExtensions = /(\.pdf|\.jpg|\.jpeg|\.png|\.PNG)$/i;
              
            if (!allowedExtensions.exec(filePath)) {
                alert('Invalid file type. Please upload a PDF or IMAGE file.');
                //this.setState({e:null})
                //console.log(this.state.file)
                //this.setState({file : this.state.file})
               // return false;
               //e.target.reset;
            } else{
              this.setState({file:e.target.files[0]})
            }
          }
  }

  onCategoryChange(e){
        this.setState({ category: e.target.value });
        console.log(e.target.value)     
  }


//   onCurrencyChange(a){
//     //a.preventDefault()
//     this.setState({ currency: a.target.value });
//     console.log(a.target.value)
// }

  fileUpload(file){
    const url = "http://localhost:5000/api/upload";
    const formData = new FormData();
    formData.append('file',file)
    console.log(this.state.category)
    console.log(this.state.currency)
    formData.append('category',this.state.category)
    formData.append('currency', this.state.currency)
    formData.append('username', currentUser.username)
   
    console.log(...formData)
    const config = {
        headers: {
            'content-type': 'multipart/form-data'
        }
    }
    return  post(url, formData,config)
   
  }

  render() {
    return (
      <form onSubmit={this.onFormSubmit}>
        <h1>File Upload</h1>
        <div>
        <input type="file" onChange={this.onChange} required/>
        </div>
      


        <div>
              <select id="2" value={this.state.category} onChange={this.onCategoryChange}  defaultValue={'DEFAULT'} required> 
                <option value="DEFAULT" disabled>Choose category</option>
                <option name="Miscellaneous"> Miscellaneous</option>
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

{/* 
              <select id= "1" value={this.state.currency} onChange={this.onCurrencyChange}  defaultValue={'DEFAULT'} required> 
                <option value="DEFAULT" disabled>Choose currency</option>
                  <option name="Dollar"> Dollar</option>
                  <option name="Indian Rupees">INR</option>
                  <option name="Euro"> Euro</option>
              </select> */}
{/* 
              <div onChange={this.onCurrencyChange}>
        <input type="radio" value="Male" name="gender" /> Male
        <input type="radio" value="Female" name="gender" /> Female
        <input type="radio" value="Other" name="gender" /> Other
      </div> */}
        </div>
       
       

        
        

        <div>
        <button type="submit">Upload</button>
        </div>
        

        {this.state.setData ? (
           <div className="ResponseData">
           {this.state.data.bill_value !== "" ? ( <p> Bill Value: {this.state.data.bill_value}</p> ) : <p> Bill Value: - </p> }
           {this.state.data.total_value !== "" ? ( <p>Monthly Expense: {this.state.data.total_value}</p>) : <p> Monthly Expense: - </p> }
           {this.state.data.category !== "" ? ( <p>Category: {this.state.data.category}</p>) : <p> Category: - </p> }
         </div>
            
          ): null }


      </form>
   )
  }
}



export default FileUpload
