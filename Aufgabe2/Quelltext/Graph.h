#ifndef GRAPH_H
#define GRAPH_H

#include <vector>
#include <string>
#include <unordered_set>
#include <boost/bimap.hpp> // Für Aliasse

typedef unsigned short int ushort;
typedef boost::bimap<int, std::string> alias_bimap;

// Farben für die Konsolenausgabe
#define RESET   "\033[0m"
#define ROT     "\033[31m"
#define GRUEN   "\033[32m"

class Graph{
public:
	Graph(ushort n_sort, ushort n_sch);
    const ushort n_schuesseln;
    const ushort n_sorten;
    const bool mehrere;
    
    std::unordered_set<ushort> preferenzen;
    void setze_preferenzen(std::string* text);
    
    alias_bimap obst_aliasse;
    
    std::vector<std::vector<bool>> kanten;
    std::vector<ushort> schuesseln;
    std::vector<ushort> sorten;
    
    void add_spiess(std::string* zahlen, std::string* namen);
    void eliminiere_kanten(std::vector<ushort>* zahlen, std::vector<ushort>* namen);
    
    void eliminiere_kanten2();
    
    void drucke_resultate();
    void drucke_resultate_v();
};

#endif
