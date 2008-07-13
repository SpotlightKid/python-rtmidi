<?python
def template_locals(template):
   for name, value in template.__dict__.iteritems():
        if not name.startswith('_') and not name.startswith('tg') and name != "std":
            yield name, repr(value)
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <title>Welcome to TurboGears</title>
</head>

<body>
    <li py:for="var,val in template_locals(self)">
       <span>${var} = ${val}</span>
        </li>
</body>

</html>
