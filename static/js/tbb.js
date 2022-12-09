// GET PROUCT OBJECT LIST FROM SERVER

async function getProductlist() {
    const response = await fetch('http://127.0.0.1:8000/main/productslist/');
    const data = await response.json();
    return data;
}

let productList = getProductlist();
// console.log(productList);

let demandList = new Array;
let postData = new Array;

// POPUP WINDOW HIDE SHOW EVENTS
const partcodeField = document.getElementById("partcode");
const screenBox = document.querySelector(".screen-box");
const popWindowCancelBtn = document.getElementById("popWindowCancelBtn")

partcodeField.addEventListener('focus',()=>{
    screenBox.style.display = "block";
    searchInput.value = "";
})

popWindowCancelBtn.addEventListener('click',()=>{
    screenBox.style.display = "none";
})

// POPUP WINDOW SEARCH AND AUTO COMELETE BOX EVENTS
const searchInput = document.querySelector("#searchinput");
const selectarea = document.querySelector('#productlist');
const autoCompleteBox = document.querySelector(".autocomplete-box");




// SHOW AUTOCOMPLETE BOX
searchInput.addEventListener("focus",()=>{
    autoCompleteBox.style.display = "block";

    // GET PRODUCT OBJECT FROM PROMISE
    productList.then((data) =>{
        let productArray = new Array;

        // CREATING DEFAULT PRODUCT LIST 
        for (element of data){
            productArray.push(`${element.partcode} | ${element.modelnumber??=""} | ${element.description}`);
        }

        // SHOW ALL PRODUCT LIST 
        let list = new Array;

        list = productArray.map((element)=>{
            partcode = element.split("|")[0].trim()
            return ` <li onclick="select(this)" data-partcode="${partcode}" > ${element} </li> `;
        })
        autoCompleteBox.innerHTML = list.join("");
        searchInput.value = "";

        // FILTER PRODUCT LIST FOR INPUT VALUE
        searchInput.addEventListener("keyup",(e)=>{
            let inputData = e.target.value;
            let emptyArray = new Array;
            if (inputData){
                emptyArray = productArray.filter((element)=>{
                    return element.toLowerCase().includes(inputData.toLowerCase())
                })

                emptyArray = emptyArray.map((element)=>{
                    partcode = element.split("|")[0].trim()
                    return ` <li onclick="select(this)" data-partcode="${partcode}" > ${element} </li> `;
                })
                autoCompleteBox.innerHTML = emptyArray.join("");
            }
        })
    })

    // GET SEARCH INPUT DATA FOR PRODUCT LIST FILTER
})

function select(element){
    element.classList.add("active")
    let selectedProduct = element.textContent;
    searchInput.value = selectedProduct;
    autoCompleteBox.style.display = "none";
}


// ADDING PRODUCT INFO TO FROMS FIELDS 
const popWindowSelectBtn = document.getElementById('popWindowSelectBtn');

popWindowSelectBtn.addEventListener('click',()=>{

    

    const selectedPartcode = document.querySelector(".active");
    const partcode = selectedPartcode.dataset.partcode;

    // GET PARTCODE QUANTITY FROM SERVER
    let url = `http://127.0.0.1:8000/main/iproduct/${partcode}`;

    fetch(url).then(res=>res.json()).then(data=> {
        let availableQuantity;
        if(data?.quantity === undefined){
            availableQuantity = 0;
        }
        else{
            availableQuantity = data.quantity;
        }


        productList.then((data)=>{
            const productObj = data.find((element)=>{
                return element["partcode"] === partcode;
            })

            // GET FORM FIELDS 
            document.querySelector('.screen-box2').style.display = "block"
            setTimeout(() => {
                partcodeField.value = productObj.partcode;
                document.getElementById("description").value = productObj.description;
                document.getElementById("availablequantity").value = availableQuantity;
                document.querySelector('.screen-box2').style.display = "none"
            }, 500);
            screenBox.style.display = "none";
            
        })
    })

})

// ADD PRODUCT OBJ TO DEMANDLIST 
const formAddBtn = document.getElementById('formAddBtn')

formAddBtn.addEventListener('click',(e)=>{
    let requiredpartcode = partcodeField.value;
    let inputQuantity = document.getElementById('quantity').value;
    let availableQuantity = parseInt(document.getElementById('availablequantity').value);
    
    productList.then((data)=>{
        const productObj = data.find((element)=>{
            return element["partcode"] === requiredpartcode;
        })
        
        if(!availableQuantity){
            console.log("product can't be added");
        }
        else{
            if(parseInt(inputQuantity)<=availableQuantity){
                if(!isPresent(requiredpartcode)){
                    // ADD DISPATCT QUANTITY
                    productObj.quantity = inputQuantity;
                    postData.push(productObj)
                    updateDemandList(inputQuantity);
                    console.log("product added to postdata and demandlist");
                }
                else{
                    console.log("product already added");
                }
            }else{
                console.log("cannot add more than avaialbe quantity")
            }
        }

        // DELETING SELECTED PRODUCT 
        
        
    })

    productForm.reset();
    e.preventDefault();
})

function updateDemandList(inputQuantity){
    const product = postData.slice(-1)[0]

    let string =` <tr id="${product.partcode}">
                    <td>${product.partcode}</td>
                    <td>5G1D5F74FSD8FSDGSD</td>
                    <td style="padding:0px 10px;">${product.modelnumber??="none"}</td>
                    <td style="width:1000px;">${product.description}</td>
                    <td> ₹ ${product.price} </td>
                    <td> ${inputQuantity} </td>
                    <td> ₹ ${inputQuantity*product.price} </td>
                    <td> <a href="javascript:void(0)" onclick="deleteProduct(${product.partcode})" >delete</a> </td>
                </tr>`

    EngineerBagList.innerHTML += string;

}

function isPresent(pn){
    return postData.some(e => e.partcode===pn)
}

function deleteProduct(pn) {
    postData.splice(postData.findIndex(e=>e.partcode===pn.id),1);
    pn.remove();
    // console.log("removed");
}


// POST DATA ON CLICKING DETERMINE BUTTON 


async function postJsonData(url = '', data = {}) {
    // Default options are marked with *
    const response = await fetch(url, {
      method: 'POST', // *GET, POST, PUT, DELETE, etc.
    //   mode: 'cors', // no-cors, *cors, same-origin
    //   cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
      credentials: 'same-origin', // include, *same-origin, omit
      headers: {
        'Content-Type': 'application/json'
        // 'Content-Type': 'application/x-www-form-urlencoded',
      },
    //   redirect: 'follow', // manual, *follow, error
    //   referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
      body: JSON.stringify(data) // body data type must match "Content-Type" header
    });
    return response.json(); // parses JSON response into native JavaScript objects
}


determineBtn = document.getElementById('determineBtn')

determineBtn.addEventListener("click",(e)=>{

    let infoObj = {
        "selected_engineer":(document.getElementById('engineer').value).toString(),
        "inspection_method":(document.getElementById('inspectiontype').value).toString()
    }
    
    // GET CURRENT URL
    const url = location.href;
    if (postData.length){
        postData.push(infoObj);
        console.log(postData);
        postJsonData(url, postData)
    .then((data) => {
        console.log(data); // JSON data parsed by `data.json()` call
    });
    }else{
        alert("No Product added !");
        return;
    }
    EngineerBagList.innerHTML = "";
    document.querySelector('.screen-box2').style.display = "block"
    setTimeout(() => {
        document.querySelector('.screen-box2').style.display = "none"
    }, 500);
    // screenBox.style.display = "none";
    // alert("Determined Successfully !!")
    e.preventDefault();

})


