function createElements(jq,nm, count){
  var teFills=(count!="None");
  var elementPare=document.getElementById("li-"+jq);

  var li=document.createElement("li");
  li.setAttribute("id", "li-"+nm);
  li.setAttribute("class","ps-2");

  var divcollapse=document.createElement("div");
  divcollapse.setAttribute("id",jq+"-collapse");
  divcollapse.setAttribute("class", "collapse pt-1");

  var ul=document.createElement("ul");
  ul.setAttribute("class", "btn_sb list-unstyled fw-normal");

  var divbutton=document.createElement("div");
  divbutton.setAttribute("id", nm);
  divbutton.setAttribute("class", "option");

  if(teFills){
    var btn=document.createElement("button");
    btn.setAttribute("id",nm);
    btn.setAttribute("class","btn_sidebar btn_outline");
    btn.setAttribute("data-bs-toggle","collapse");
    btn.setAttribute("data-bs-target","#"+nm+"-collapse");
    btn.setAttribute("aria-expanded","false");
    btn.innerHTML="X";
    divbutton.appendChild(btn);
  }

  var a=document.createElement("a");
  a.setAttribute("class","nav-link");
  a.setAttribute("href","#");
  if(!teFills){
    a.innerHTML="➤ "+nm;
  }else{
    a.innerHTML=nm;
  }
  divbutton.appendChild(a);

  divcollapse.appendChild(divbutton);
  divcollapse.appendChild(ul);
  li.appendChild(divcollapse);
  elementPare.appendChild(li);
}
function addFunctiontoButtons(){
  var buttons=document.querySelectorAll(".btn_sidebar");
  buttons.forEach((bt)=>{
    bt.addEventListener('click',
      ()=>{
        hideChildren(bt.id);
    })
  });
}
function hideChildren(nm){
  var elementCalled=document.getElementById("li-"+nm);
  var fills = elementCalled.getElementsByClassName("collapse");

  if(fills.length>0){
    for(var i=1; i<fills.length;i++){
      fills[i].classList.remove("show");
   }
  }
}
