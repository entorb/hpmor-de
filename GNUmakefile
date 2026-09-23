# Build the PDFs and the e-books locally. Releases are made by GitHub Actions.

JACKETS = $(addprefix layout/hpmor-dust-jacket-,1 2 3 4 5 6)

all: ebooks

pdf:
	sh scripts/make_pdf-1-vol.sh

volumes:
	sh scripts/make_pdf-6-vol.sh

pdf-all:
	sh scripts/make_pdf-all.sh

# A dust jacket reads its volume's PDF to get the page count, hence pdf-all.
jackets: pdf-all
	latexmk $(JACKETS)

ebooks: pdf
	sh scripts/make_ebooks.sh

clean:
	latexmk -C

.PHONY: all pdf volumes pdf-all jackets ebooks clean

# Never run two latexmk processes in this directory at once: all seven
# documents \include the same chapters and write the same chapters/*.aux.
.NOTPARALLEL:
