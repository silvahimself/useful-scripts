import sys, getopt
import random
import string
import uuid
 
def random_string_generator(str_size, allowed_chars):
    return ''.join(random.choice(allowed_chars) for x in range(str_size))
 
chars = string.ascii_letters + "1234567890@#$%&"

size = 12

def main(argv):
    size = 12
    generate_guid = False
    
    try:
        opts, args = getopt.getopt(argv,"hs:g",["size=","guid"])
    except getopt.GetoptError:
        print('rstring.py -s <stringsize> | --guid')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('rstring.py -s <stringsize> | --guid')
            sys.exit()
        elif opt in ("-s", "--size"):
            size = arg
        elif opt in ("-g", "--guid"):
            generate_guid = True
    
    if generate_guid:
        print(str(uuid.uuid4()))
    else:
        print(random_string_generator(int(size), chars))


if __name__ == "__main__":
   main(sys.argv[1:])