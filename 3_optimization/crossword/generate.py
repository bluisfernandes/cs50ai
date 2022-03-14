import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.domains:
            domain = self.domains[var].copy()
            for word in domain:
                if len(word) != var.length:
                    self.domains[var].remove(word)        
        
    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # position of overlaps letters
        px, py = self.crossword.overlaps[x,y]
        letters_y = set(word[py] for word in self.domains[y])
        
        revised = False
        domain = self.domains[x].copy()
               
        for word in domain:
            # if letters is not coincidents
            if word[px] not in letters_y:
                self.domains[x].remove(word)
                revised = True
        return revised


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs == None:
            queue = set(arc for arc in self.crossword.overlaps if self.crossword.overlaps[arc] is not None)
        else:
            queue = arcs
        while queue:
            x,y = queue.pop()
            if self.revise(x,y):
                if len(self.domains[x]) == 0:
                    return False
                for z in self.crossword.neighbors(x):
                    if z != y:
                        queue.add((z, x))
        return True
        # raise NotImplementedError

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for var in self.crossword.variables:
            if var not in assignment:
                return False
        return True
        # raise NotImplementedError

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        values = assignment.values()
        
        # checks repeated words
        if len(values) != len(set(values)):
            return False
        
        for assigned in assignment:
            # checks words length
            if assigned.length == len(assignment[assigned]):
                return False

            # checks the neighbors
            for neigb in self.crossword.neighbors(assigned):
                if neigb in assignment:
                    pos_assign, pos_neigb = self.crossword.overlaps[(assigned,neigb)]
                    # check the charachter in "pos_n"
                    if assignment[assigned][pos_assign] != assignment[neigb][pos_neigb]:
                        return False
        return True


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        domains = {word :0 for word in self.domains[var]}
        neighbors = self.crossword.neighbors(var)
        valid_neighbors = neighbors - set(assignment)

        for neighbor in valid_neighbors:
            # position of overlaps letters
            pos_var, pos_nei = self.crossword.overlaps[var,neighbor]

            for word in domains:
                letter_var = word[pos_var]
                for neig_domain in self.domains[neighbor]:
                    letter_nei = neig_domain[pos_nei]

                    #if word incompatible with each neighbordomais count +1
                    if letter_nei == letter_var:
                        domains[word] += 1 

        return sorted(domains, key = domains.__getitem__)
   

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        return assignment[0 ]
        # raise NotImplementedError

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # for word in self.crossword.variables:
        #     if word.length == 3:
        #         assignment[word] = "SIX"

        x = Variable(0, 1, 'down', 5)
        
        
        
        # assignment[x] = "SEVEN"
        x = Variable(1, 7, 'down', 7)
        assignment[x] = "MINIMAX"

        # y = Variable(2, 1, 'across', 12)
        # assignment[y] = "INTELLIGENCE"

        y = Variable(4, 4, 'across', 5)
        assignment[y] = "LOGIC"

        # w = Variable(6, 5, 'across', 6)
        w = Variable(2, 1, 'across', 12)
        
        print(self.order_domain_values(w, assignment))
        # print(f"{self.assignment_complete(assignment)=}")
        # print(f"{self.consistent(assignment)=}")
        # print(self.crossword.variables)
        return assignment
        # raise NotImplementedError


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    
    # ***
    # print(f"{crossword.variables=}")
    # print(f"{creator.domains=}")
    for variable, domain in creator.domains.items():
        print(" ",variable, ":\t", domain)
    # print(f"{crossword.neighbors(Variable(0, 1, 'across', 3))=}")
    # print(f"{crossword.overlaps[Variable(1, 4, 'down', 4),Variable(4, 1, 'across', 4)]=}")
    # ***

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
