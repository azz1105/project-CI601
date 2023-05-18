	<html>
<body>
	Thank you <?php echo $_POST['name'];?><br> for submitting your information. We will contact you in your email: <?php echo $_POST['Email'] ;?>.
	

<?php 
 	$name = $_POST['name'];
 	$visitor_email = $_POST['Email'];
 	$message = $_POST['message'];


 	$email_form = 'aziz.aljehani99@gmail.com';

 	$email_subject = "New form submission";

 	$email_body = "User Name: $name.\n".
 					"User Email: $visitor_email.\n".
 						"User Message: $message.\n";



 	$to = "aziz.aljehani99@gmail.com";

 	$headers = "from: $email_form \r\n";

 	$headers .= "reply-To: $visitor_email \r\n"; 

 	mail($to,$email_subject,$email_body,$headers);

 	header("Location: contactme.html");?>
</body>
</html> 
