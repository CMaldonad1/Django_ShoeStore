function createElements(categ){
  var teFills=(categ.count!="None");
  var elementPare=document.getElementById("li-"+categ.jq);

  var li=document.createElement("li");
  li.setAttribute("id", "li-"+categ.nm);
  li.setAttribute("class","ps-2");

  var divcollapse=document.createElement("div");
  divcollapse.setAttribute("id",categ.jq+"-collapse");
  divcollapse.setAttribute("class", "collapse pt-1");

  var ul=document.createElement("ul");
  ul.setAttribute("class", "btn_sb list-unstyled fw-normal");

  var divbutton=document.createElement("div");
  divbutton.setAttribute("id", "div-"+categ.nm);
  divbutton.setAttribute("class", "option");

  if(teFills){
    var btn=document.createElement("button");
    btn.setAttribute("id",categ.nm);
    btn.setAttribute("class","btn_sidebar btn_outline");
    btn.setAttribute("data-bs-toggle","collapse");
    btn.setAttribute("data-bs-target","#"+categ.nm+"-collapse");
    btn.setAttribute("aria-expanded","false");
    btn.innerHTML="★";
    divbutton.appendChild(btn);
  }

  var a=document.createElement("a");
  a.setAttribute("class","nav-link");
  a.setAttribute("href","/cataleg/"+categ.id);
  if(!teFills){
    a.innerHTML=" ➤ "+categ.nm;
  }else{
    a.innerHTML=categ.nm;
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
  verifyIfSelected(nm);
}
function verifyIfSelected(nm){
  var selected=document.getElementById(nm);

  if(selected.classList.contains("selected")){
    selected.classList.remove("selected");
  }else{
    selected.classList.add("selected");
  }


}
function createProductCard(product){
  console.info(product.prodId)
  var cataleg= document.getElementById("prodcat");
  var elementPare=document.getElementById(product.prodId);
  var container;
  if(elementPare==null){
    container=document.createElement("div");
    container.setAttribute("id", product.prodId)
    container.setAttribute("class","col-10 col-sm-5 col-md-4 col-lg-3 p-2");
  
    var img= document.createElement("img");
    img.setAttribute("class","card-img-top");
    img.setAttribute("alt", "Product Image")
    img.setAttribute("src","https://images.unsplash.com/photo-1542291026-7eec264c27ff?crop=entropy&amp;cs=tinysrgb&amp;fit=max&amp;fm=jpg&amp;ixid=M3w0NzEyNjZ8MHwxfHNlYXJjaHwxfHxzaG9lfGVufDB8MHx8fDE3MjEwNDEzNjd8MA&amp;ixlib=rb-4.0.3&amp;q=80&amp;w=1080")

    var card=document.createElement("div");
    card.setAttribute("class","card");

    var body=document.createElement("div");
    body.setAttribute("class","card-body");

    var title=document.createElement("h5");
    title.setAttribute("class","card-title");
    title.innerHTML=product.prod;

    var descr=document.createElement("p");
    descr.setAttribute("class","card-text");
    descr.innerHTML=product.descr;

    body.appendChild(title);
    body.appendChild(descr)

    card.appendChild(img);
    card.appendChild(body);
    
    container.appendChild(card);
    cataleg.appendChild(container);
  }

}