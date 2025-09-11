// creació de l'estructura de l'arbre d'elements
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

  var a=document.createElement("a");
  a.setAttribute("class","nav-link");
  a.setAttribute("href","/cataleg/"+categ.id);
  if(!teFills){
    a.innerHTML=" ➤ "+categ.nm;
  }else{
    a.innerHTML=" ★ "+categ.nm;
  }
  divbutton.appendChild(a);

  divcollapse.appendChild(divbutton);
  divcollapse.appendChild(ul);
  li.appendChild(divcollapse);
  elementPare.appendChild(li);
}
function showVariant(ev){
  console.info(ev);
  var idElement=ev.target.id;
  var preu_Dto=ev.target.alt;
  var url=ev.target.src;
  var id=idElement.substring(0, idElement.indexOf("-"))
  // seleccionem totes les variants del producte per a treure-li la clase imgSel
  var imgVar=document.getElementById("prodVariants-"+id).getElementsByTagName('img');
  for(var i = 0; i < imgVar.length; i++) {
    imgVar[i].classList.remove('imgSel');
  }
  // li agregem al item que actualment ha sigut clicat
  document.getElementById(idElement).classList.add('imgSel');
  //extrayem la informació que hi ha en els camps de la imatge per ficar-la a la tarjeta
  var pos=preu_Dto.indexOf("-");
  var pos2=preu_Dto.indexOf("_");
  var preu=preu_Dto.substring(0,pos);
  var dto=preu_Dto.substring(pos+1,pos2);
  var variant=preu_Dto.substring(pos2+1);
  var preuElement=document.getElementById("preu-"+id);
  var dtoElement=document.getElementById("dto-"+id);
  var btnElement=document.getElementById("btn-"+id);
  dtoElement.classList.remove("d-flex");
  dtoElement.classList.remove("d-none");
  document.getElementById("imgtop-"+id).setAttribute("src", url);
  if(dto>0){
    dtoElement.classList.add("d-flex")
    dtoElement.querySelector("span").innerText=(dto*100)+"% dto.";
    preuElement.innerHTML="<b>Preu:</b> "+ (preu*(1-dto)).toFixed(2)+"€ <s>"+preu+"€</s>";
  }else{
    dtoElement.classList.add("d-none")
    preuElement.innerHTML="<b>Preu:</b> "+preu+"€";
  }
  btnElement.setAttribute("href","/info/"+variant);
}
function hideFiltres(name){
  var filtres=document.getElementById(name);
  var button=document.getElementById("hide"+name);
  var hidden=filtres.hidden
  
  button.classList.toggle("btn_outline");
  button.classList.toggle("btn_normal");
  if(name=="filtreCataleg"){
    scrollLlistatVariants(hidden)
    filtres.parentElement.style.overflowY=(hidden)?"scroll":"hidden";
  }
  filtres.hidden=!hidden;
}
function scrollLlistatVariants(hidden){
  var overflowY="hidden";
  var maxHeight="100%";
  var listvar=document.getElementById("listVar")
  if(hidden){
    overflowY="scroll";
    maxHeight="50%";
  }
  listvar.style.overflowY=overflowY;
  listvar.style.maxHeight=maxHeight;
}
function setImage(event, src){
  document.getElementById("imgGran").setAttribute("src",src)
}
async function changeVariant(event) {
  try {
    id=event.target.id;
    const response = await fetch('http://127.0.0.1:8000/variantInfo/', 
      {method: "POST",
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          'idVar': id
        })
      }
    );
    imgVar=document.getElementById('varLlistat').getElementsByTagName('img');
    for(var i = 0; i < imgVar.length; i++) {
      imgVar[i].classList.remove('imgSel');
    }
    document.getElementById(id).classList.add('imgSel');
    const data = await response.json();
    if(data.length==0){
      alert("No s'ha trobat cap resultat per la busqueda");
    }else{
      informationChangeVar(data)
    }
  } catch (error) {
      alert(error);
  }
}
function informationChangeVar(data){
  generarPreuInfo(data);
  document.getElementById("imgGran").setAttribute("src","/static/"+data.imatges[0])
  document.getElementById("variantID").innerHTML=data.id;
  document.getElementById("model").innerHTML="<b>Marca: </b>"+data.nom
  generarImatgesPetites(data.imatges)
  generarTallesSelector(data.talles);
  activaBotoCarro();
}
function generarTallesSelector(talles){
  var pare=document.getElementById("sTalles");
  pare.innerHTML="";
  var fill=document.createElement("option");
  fill.value= 0;
  fill.text="-";
  pare.appendChild(fill);
  for(i=0; i<talles.length;i++){
    console.info(talles[i].tNom)
      var opt=fill.cloneNode();
      var qty= talles[i].qty;
      opt.value= talles[i].tId;
      opt.text=talles[i].tNom+" (Max Uds: "+ qty+")";
      if(qty==0){
        opt.disabled=true;
      }
      pare.appendChild(opt);
  }
}
function generarImatgesPetites(imatges){
  var pare=document.getElementById("imgProd");
  pare.innerHTML="";
  for(i=0; i<imatges.length; i++){
    var el=document.createElement("img");
    el.setAttribute("src","/static/"+imatges[i]);
    el.setAttribute("class","thumbnail rounded active");
    el.addEventListener("mouseenter",(ev)=>{
      setImage(ev, ev.target.src)
    })
    pare.appendChild(el);
  }
}
function generarPreuInfo(data){
  var pare=document.getElementById("preuSection");
  pare.innerHTML="";
  var preu=data.preu
  var preu_dto=data.preu;
  var dto=data.dto;

  var divPreu=document.createElement("div");
  var spanPreu1=document.createElement("span");
  spanPreu1.setAttribute('class','h4');
  spanPreu1.innerText="Preu: ";

  var spanPreu2=document.createElement("span");
  spanPreu2.setAttribute('id','preuvar');
  spanPreu2.setAttribute('class','text-muted');

  divPreu.appendChild(spanPreu1);
  pare.appendChild(divPreu);
  if(dto>0){
    preu_dto=(data.preu*(1-dto)).toFixed(2);
    spanPreu2.innerHTML=preu_dto+"€ <s>"+preu+"€</s>";

    var divDto= document.createElement("div");
    divDto.setAttribute('class','ps-4');

    var spanDto1=document.createElement("span");
    spanDto1.setAttribute('class','h5');
    spanDto1.innerText="Dto: "

    var spanDto2=document.createElement("span");
    spanDto2.setAttribute('id','dtovar');
    spanDto2.setAttribute('class','text-muted');
    spanDto2.innerText=dto*100+"%";

    divDto.appendChild(spanDto1);
    divDto.appendChild(spanDto2);
    pare.appendChild(divDto);
  }else{
    spanPreu2.innerText=preu+"€";
  }
  divPreu.appendChild(spanPreu2);
}
async function cistella(){
  var e=document.getElementById("sTalles");
  var index=e.selectedIndex
  var id=e.options[index].value;
  var qty=document.getElementById("sQty").value
  try {
    const response = await fetch('http://127.0.0.1:8000/add/', 
      {method: "POST",
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          'var': id,
          'qty': qty,
        })
      }
    );
    var data = await response.json();
    var items = data.cistella;
    var newqty= data.qty;
    if(items==-1){
      activarModal();
    }else{
      actualitzarCistella(items);
      updateDropDownPosition(e,index,newqty)
    }
  } catch (error) {
    alert("Error en accedir a la informació de la cistella");
  }
}
function actualitzarCistella(items){
  var elementExists=document.getElementById('cistella');
  if(!elementExists){
    var cistella=document.createElement("div");
    cistella.setAttribute('id','cistella');
    cistella.setAttribute('class','check position-absolute');
    document.getElementById('divCistella').appendChild(cistella);
  }
  document.getElementById('cistella').innerText = items;
}
function updateDropDownPosition(e,index,qty){
  var tallaSel=e.options[index].text
  var qtyTalla=tallaSel.substring(tallaSel.indexOf(":")+2, tallaSel.length-1);
  e.options[index].text=tallaSel.replace(qtyTalla, qty);

  if(qty==0){
    e.options[index].disabled;
    document.getElementById("addCart").disabled=true;
    document.getElementById("incr").disabled=true;
    document.getElementById("decr").disabled=true;
    document.getElementById("sQty").value=0;
  }
}
async function incrStock(id){
  try {
    const response = await fetch('http://127.0.0.1:8000/incrStock/', 
      {method: "POST",
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          'prod': id,
          'varid': document.getElementById('variantID').innerText
        })
      }
    );
    const data = await response.json();
    generarTallesSelector(data);
    activaBotoCarro();
    alert("Totes les talles del model han sigut incrementades");
  } catch (error) {
    alert(error);
  }
}
async function activarModal(){
  var myModal = new bootstrap.Modal(document.getElementById('login'), {});
  myModal.show();
  const response = await fetch('http://127.0.0.1:8000/eliminarMissatge/') 
}
function desfiltra(){
  document.getElementById('pmin').value="";
  document.getElementById('pmax').value="";
  document.getElementById('nomf').value="";
  document.querySelectorAll('input[name=chktalla]:checked').forEach(ckbx => ckbx.checked=false);
  filtre();
}
function amagar_mostrarChivato(pmin,pmax,nom,talles){
  var chivatoPreu=(pmin !="")?false:(pmax != "")?false:true;
  var chivatoNom=(nom !="")?false:true;
  var chivatoTalles=(talles !="")?false:true;
  var chivatoFiltres=true;
  
  document.getElementById("nomGlow").hidden=chivatoNom;
  document.getElementById("preuGlow").hidden=chivatoPreu;
  document.getElementById("tallaGlow").hidden=chivatoTalles;

  if(!chivatoNom || !chivatoPreu || !chivatoTalles){
    chivatoFiltres=false;
  }
  document.getElementById("filterGlow").hidden=chivatoFiltres;
}
async function filtre(){
  var pmin=document.getElementById('pmin').value;
  var pmax=document.getElementById('pmax').value;
  var nom=document.getElementById('nomf').value;
  var ckbx=document.querySelectorAll('input[name=chktalla]:checked');
  var talles="";

  //recorrem els checkboxs marcats i fem un array de talles per a pasar-la a la API
  if(ckbx.length>0){
    talles=ckbx[0].value;
    for(var i=1; i < ckbx.length; i++){
      talles+=","+ckbx[i].value;
    }
  }
  //si el preu minim es superior al máxim es fará que el preu maxim sigui igual al preu minim
  if(pmin>pmax &&  pmin!='' && pmax!=''){
    pmax=pmin
    document.getElementById('pmax').value=pmin
  }

  amagar_mostrarChivato(pmin,pmax,nom,talles);

  try {
    const response = await fetch('http://127.0.0.1:8000/filtrar/', 
      {method: "POST",
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          'nom': nom,
          'pmin': pmin,
          'pmax': pmax,
          'talles':talles
        })
      }
    );
    if (response.ok) {
      // Get the HTML response
      const htmlContent = await response.text();
      // Insert the HTML response into a specific element in the DOM
      document.getElementById('prodcat').innerHTML = htmlContent;
    }else{
      alert("No s'ha trobat cap resultat per al filtre indicat")
    }
  } catch (error) {
      alert(error);
  }
}
function activaBotoCarro(){
  var disabled=true;
  var e=document.getElementById("sTalles");
  var btn=document.getElementById("addCart");
  var qty=document.getElementById("sQty");
  var tallaSel=e.options[e.selectedIndex].text
  var qtyTalla=tallaSel.substring(tallaSel.indexOf(":")+2, tallaSel.length-1);
  var btns=document.getElementsByClassName("incrdcr");
  
  if(e.options[e.selectedIndex].value != 0){
    qty.setAttribute('max',qtyTalla);
    if(qty.value>qtyTalla){
      qty.value=qtyTalla;
    }
    disabled=false;
  }

  btn.disabled=disabled;
  for(i=0;i<btns.length;i++){
    btns[i].disabled=disabled;
  }

}
async function updateItemCistell(id){
  var index=id.indexOf("_");
  var accio=id.substring(0, index);
  var variant=id.substring(index+1)
  var element=document.getElementById("qty_"+variant);
  var currValue=parseInt(element.value);
  var incrDecr=1
  if(accio=="dcr"){
    incrDecr=-1
  }
  element.value=currValue+incrDecr
  const response = await fetch('http://127.0.0.1:8000/updateCistella/', 
    {method: "POST",
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        'var': variant,
        'qty': element.value,
      })
    }
  );
}
function verifyTarjeta(){
  var cardImg=""
  var err=""
  var e=document.getElementById("numTarj");
  var tarjeta=e.value;
  var visaRegex=/^4[0-9]{12}(?:[0-9]{3})?$/;
  var amexRegex=/^3[47][0-9]{13}$/;
  var mastRegex=/^(5[1-5][0-9]{14}|2(22[1-9][0-9]{12}|2[3-9][0-9]{13}|[3-6][0-9]{14}|7[0-1][0-9]{13}|720[0-9]{12}))$/;
  // Visa
  if(visaRegex.exec(tarjeta)){
    cardImg="https://mdbcdn.b-cdn.net/wp-content/plugins/woocommerce-gateway-stripe/assets/images/visa.svg"
  // American Express
  }else if(amexRegex.exec(tarjeta)){
    cardImg="https://mdbcdn.b-cdn.net/wp-content/plugins/woocommerce-gateway-stripe/assets/images/amex.svg"
  // Mastercard
  }else if(mastRegex.exec(tarjeta)){
    cardImg="https://mdbcdn.b-cdn.net/wp-content/plugins/woocommerce-gateway-stripe/assets/images/mastercard.svg"
  }else{
    err="Tarjeta incorrecta! Revisa el número";
  }
  if(err.length>0){
    e.classList.add("inputErr")
  }else{
    e.classList.add("inputOk")
  }
  document.getElementById("tarErr").innerText=err;
  document.getElementById("tarjeta").setAttribute('src',cardImg);
  return err.length;
}
function verifyCaducitat(){
  var regex=/^(0[1-9]|1[0-2])\/\d{4}$/
  var e=document.getElementById('caducitat');
  var caducitat=e.value;
  var err=""
  if(regex.exec(caducitat)){
    var period= new Date();
    var anyAct=period.getFullYear();
    var mesAct=period.getMonth();
    var pos=caducitat.indexOf("/");
    var mes=caducitat.substring(0,pos);
    var any=caducitat.substring(pos+1);
    
    if(any<anyAct || mes<mesAct){
      err="Tarjeta caducada!"
    }
  }else{
    err="Caducitat incorrecta!"
  }

  if(err.length>0){
    e.classList.add("inputErr")
  }else{
    e.classList.add("inputOk")
  }
  
  document.getElementById("cadErr").innerText=err;
  
  return err.length;

}
function verifyCvv(){
  var regex=/^[0-9]{3}$/
  var e=document.getElementById('cvv');
  var cvv=e.value;
  var err=""
  
  if(!regex.exec(cvv)){
    err="Codi incorrecte!";
    e.classList.add("inputErr")
  }else{
    e.classList.add("inputOk")
  }
  document.getElementById("cvvErr").innerText=err;
  return err.length;
}
function verifyNom(){
  var e=document.getElementById('tarjetaNom');
  var tn=e.value;
  var err="";
  e.classList.remove("inputOk","inputErr");
  if(tn.length<15){
    err="El nom es incorrecte!"
    e.classList.add("inputErr")
  }else{
    e.classList.add("inputOk")
  }
  document.getElementById("tarjetaNomErr").innerText=err;
  return err.length;
}
async function callPagament(){
  var err=0;
  err+=verifyTarjeta();
  err+=verifyCaducitat();
  err+=verifyCvv();
  err+=verifyNom();
  if(err==0){
    var loading= document.getElementById("loading");
    loading.style.display="flex";
    const response = await fetch('http://127.0.0.1:8000/realitzarPagament/',
      {method: "POST",
          headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
          },
      });
    if (response.ok) {
      // Get the HTML response
      const htmlContent = await response.text();
      // Insert the HTML response into a specific element in the DOM
      document.getElementById('contingut').innerHTML = htmlContent;
    }
  } else {
    document.getElementById('pagamentErr').innerText="La informació de pagament es incorrecta. Revisala."
  }

}
