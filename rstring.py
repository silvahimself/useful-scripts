import sys, getopt
import random
import string
 
def random_string_generator(str_size, allowed_chars):
    return ''.join(random.choice(allowed_chars) for x in range(str_size))
 
chars = string.ascii_letters + "1234567890@#$%&"

size = 12

def main(argv):
    size = 12
    
    try:
        opts, args = getopt.getopt(argv,"hs:",["size="])
    except getopt.GetoptError:
        print ('rstring.py -s <stringsize>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('rstring.py -s <stringsize>')
            sys.exit()
        elif opt in ("-s", "--size"):
            size = arg
        
    print(random_string_generator(int(size), chars))


if __name__ == "__main__":
   main(sys.argv[1:])