function createElements(categ){
  var teFills=(categ.count!="None");
  var elementPare=document.getElementById("li-"+categ.jq);

  var li=document.createElement("li");
  li.setAttribute("id", "li-"+categ.nm);
  li.setAttribute("class","ps-2");

  var divcollapse=document.createElement("div");
  divcollapse.setAttribute("id",categ.jq+"-collapse");
  divcollapse.setAttribute("class", "collapse pt-1 show");

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
  var elementPare=document.getElementById(product.prodId);
  var imatge;
  if(elementPare==null){
    imatge="https://contents.mediadecathlon.com/p2616911/k$005506460860670fe53bdfa2f971c8d3/sq/zapatillas-caminar-adidas-vl-court-30-hombre-blanco.jpg?format=auto&f=646x646";
    creacioElementPare(product, imatge);
  }else{
    imatge="https://contents.mediadecathlon.com/p2698107/k$091a49ae006f2ebc891f44750f165a51/sq/zapatillas-adidas-advantage-base-20-hombre-negro.jpg?format=auto&f=646x646";
    zonavariants=document.getElementById("variant-"+product.prodId);
    creacioMiniImatge(zonavariants, imatge, product);
  }

}
function creacioElementPare(product, imatge){
  var cataleg= document.getElementById("prodcat");
  var container=document.createElement("div");
  container.setAttribute("id", product.prodId)
  container.setAttribute("class","col-10 col-sm-6 col-lg-3 p-2");

  var img= document.createElement("img");
  img.setAttribute("id","imgtop-"+product.prodId);
  img.setAttribute("class","card-img-top");
  img.setAttribute("alt", "Product Image");
  img.setAttribute("src", imatge);

  var card=document.createElement("div");
  card.setAttribute("class","card");

  var cardbody=document.createElement("div");
  cardbody.setAttribute("class","card-body");

  var cardtitle=document.createElement("h5");
  cardtitle.setAttribute("class","card-title");
  cardtitle.innerHTML=product.prod;

  var descr=document.createElement("p");
  descr.setAttribute("class","card-text");
  descr.innerHTML=product.descr;

  cardbody.appendChild(cardtitle);
  cardbody.appendChild(descr)

  card.appendChild(img);
  card.appendChild(cardbody);
  
  var options=document.createElement("div");
  options.setAttribute("id","options-"+product.prodId);
  options.setAttribute("class","d-flex flex-column align-items-center");

  var preu=document.createElement("div");
  preu.setAttribute("id","preu-"+product.prodId);
  preu.setAttribute("class","col-11");
  preu.innerHTML="<b>Preu:</b> "+product.preu+" €";

  options.appendChild(preu);

  var zonavariants=document.createElement("div");
  zonavariants.setAttribute("id","variant-"+product.prodId);
  zonavariants.setAttribute("class","d-flex flex-row align-items-start p-2");

  creacioMiniImatge(zonavariants, imatge, product);

  options.appendChild(zonavariants);
  
  card.appendChild(options);

  var cardFooter=document.createElement("div");
  cardFooter.setAttribute("id","foot-"+product.prodId);
  cardFooter.setAttribute("class","card-footer d-flex justify-content-between bg-light");

  var veureprod=document.createElement("button");
  veureprod.setAttribute("class","btn btn_normal btn-sm");
  veureprod.innerHTML="Veure";

  cardFooter.appendChild(veureprod);
  card.appendChild(cardFooter);
  
  container.appendChild(card);
  cataleg.appendChild(container);

  return container;
}
function creacioMiniImatge(zonavariants, imatge, product){
  var img= document.createElement("img");
  img.setAttribute("id",product.prodId)
  img.setAttribute("class","col-2 m-1");
  img.setAttribute("alt", product.preu+"-"+product.dto);
  img.setAttribute("src", imatge);
  img.addEventListener('mouseover', (ev)=>{
    var element={
      "id":ev.explicitOriginalTarget.id,
      "preu":ev.explicitOriginalTarget.alt,
      "url":ev.explicitOriginalTarget.src
    }
    hoverImage(element);
  });
  zonavariants.appendChild(img);
}
function hoverImage(element){
  var pos=element.preu.indexOf("-");
  var preu=element.preu.substring(0,pos);
  var dto=element.preu.substring(pos+1)*100;
  document.getElementById("imgtop-"+element.id).setAttribute("src", element.url);
  document.getElementById("preu-"+element.id).innerHTML="<b>Preu:</b> "+preu+" €";
}