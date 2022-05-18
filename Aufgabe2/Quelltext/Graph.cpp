#include "Graph.h"
#include <iostream>
using namespace std;

// Konstruktor baut Liste mit Kanten.  (alles nach ":" ist die initializer list (richtig coole Sache))
Graph::Graph(ushort n_sort, ushort n_sch):kanten(n_schuesseln, vector<bool>(n_sorten, true)),
                                          schuesseln(n_sch),
                                          sorten(n_sort),
                                          n_sorten(n_sort),
                                          n_schuesseln(n_sch),
                                          mehrere(n_sort != n_sch){
    // Erstelle die Menge Schüsseln und die Menge Sorten (Für größere Schnelligkeit als Vektor implementiert)
    for (int i = 0; i < n_schuesseln; i++) schuesseln[i] = i;
    for (int i = 0; i < n_sorten; i++) sorten[i] = i;
}

// Füllt Donalds Preferenzen &%?ßüöä
void Graph::setze_preferenzen(string* text){
    stringstream strstm(*text);
    string tmp;
    while (strstm >> tmp)
    {
        // obst_aliasse ist ein bidirectional map <int, string>
        obst_aliasse.insert({obst_aliasse.size(), tmp});
        int x = obst_aliasse.right.at(tmp);
        preferenzen.insert(x);
    }
}

// Fügt einen Spieß hinzu
void Graph::add_spiess(string* zahlen, string* namen){
    string tmp; 
    int sn;
    vector<ushort> set_zahlen, set_namen;
    
    // Schüsselnummern
    stringstream strstm(*zahlen);
    while (strstm >> tmp)
    {
        sn = stoi(tmp);
        if (sn > n_schuesseln) throw(tmp); // Überprüfe die Gültigkeit der Eingabe.
        set_zahlen.push_back(sn - 1); // -1 passt an Computerzählweise an.
    }
    strstm.clear();
    
    // Obstsorten
    strstm.str(*namen);
    while (strstm >> tmp)
    {
        // ergänze obst_aliasse
        if (obst_aliasse.size() < n_sorten) {
            obst_aliasse.insert({obst_aliasse.size(), tmp});  // Verbessern
        }
        set_namen.push_back(obst_aliasse.right.at(tmp));
    }
    // Sortiere die Vektoren, um das Eliminieren von Kanten zu ermöglichen.
    sort(set_zahlen.begin(), set_zahlen.end());
    sort(set_namen.begin(), set_namen.end());
    eliminiere_kanten(&set_zahlen, &set_namen);
}

// Setzt unmögliche Kanten auf 0
void Graph::eliminiere_kanten(vector<ushort>* zahlen, vector<ushort>* namen){
    vector<ushort> andere_zahlen, andere_namen;
    
    // Falls nicht mehrere Schüsseln pro Sorte erlaubt sind:
    if (!mehrere){
        // alle Schüsseln, die nicht in der betrachteten Menge sind (kommen in andere_zahlen)
        set_difference(schuesseln.begin(), schuesseln.end(), (*zahlen).begin(), (*zahlen).end(),
                       inserter(andere_zahlen, andere_zahlen.end()));
        for (auto i : andere_zahlen){
            for (auto j : *namen) kanten[i][j] = false;
        }
    }
    
    // alle Sorten, die nicht in der betrachteten Menge sind (kommen in andere_namen)
    set_difference(sorten.begin(), sorten.end(), (*namen).begin(), (*namen).end(),
                   inserter(andere_namen, andere_namen.end()));
    
    // setze alle ähnlichen Kanten auf 0
    for (auto i : *zahlen)
    {
        for (auto j : andere_namen) kanten[i][j] = false;
    }
}

// Nur für die Option mit mehreren Schüsseln pro Sorte
void Graph::eliminiere_kanten2(){
    int einzig_moeglich; bool contains_uncertain = true;
    
    // Wiederhole solange es nicht eindeutige Zuordnungen gibt oder
    // oft genug um sicher zu sein, dass die maximale Gewissheit erreicht wurde.
    for (int count = 0; count < n_sorten && contains_uncertain; count++)
    {
        contains_uncertain = false;
        
        // Für jede Sorte
        for (auto i : sorten)
        {
            einzig_moeglich = -1; // zurücksetzen
            // Überprüfe, ob es für eine Sorte mehrere mögliche Schüsseln gibt.
            for (auto j : schuesseln)
            {
                if (kanten[j][i]){
                    if (einzig_moeglich < 0){
                        einzig_moeglich = j;
                    }
                    else{
                      einzig_moeglich = -1;
                      contains_uncertain = true;
                      break;
                    }
                }
            }
            if (einzig_moeglich < 0) continue;
            // Wenn ja, setze Alle anderen Kanten, die mit der Schüssel verbunden sind, auf 0
            for (auto k : sorten)
            {
                if (k == i) continue;
                kanten[einzig_moeglich][k] = false;
            }
        }
    }
}

void Graph::drucke_resultate(){
    string ausg_eind, ausg_neind, zeile_neind, name_sorte;
    
    for (auto i : schuesseln)
    {
        bool nur_pref = true, keine_pref = true; // lieber true oder false?
        zeile_neind = ("Schüssel " + to_string(i+1) + ": ");
        
        for (auto j : sorten)
        {
            if (!kanten[i][j]) continue; // Falls Zuordnung nicht möglich, weiter
            
            // Differenziere zwischen Wunschsorten und anderen
            if (preferenzen.find(j) == preferenzen.end()){
                nur_pref = false;
                try{
                    // Wenn die Sorte nicht in einem der Spieße war, kann dies zu Fehlern führen.
                    name_sorte = obst_aliasse.left.at(j);
                } catch(...){
                    name_sorte = "Unbekannt";
                }
                zeile_neind += (ROT + name_sorte + RESET + ", ");
            }
            else{
                keine_pref = false;
                zeile_neind += (obst_aliasse.left.at(j) + ", ");
            }
        }
        if (nur_pref) ausg_eind += (to_string(i+1) + ", ");
        else if (!keine_pref){
            zeile_neind.resize(zeile_neind.size() - 2);
            ausg_neind += (zeile_neind + "\n");
        }
    }
    if (ausg_eind.size() > 1){
        ausg_eind.resize(ausg_eind.size()-2); // entfernt das letzte Komma
        cout << "Schüssel(n): { " << ausg_eind << " }\n\n";
        
    }
    if (ausg_neind.size() > 0) cout << "Diese Schüsseln können nicht eindeutig einer Wunschsorte zugewiesen werden:\n"
                                    << ausg_neind << "\n";
    return;
}
void Graph::drucke_resultate_v(){
    string name_sorte;
    
    for (auto i : schuesseln)
    {
        cout << "Schüsssel " << i+1 << ": ";
        for (auto j : sorten)
        {
            if (!kanten[i][j]) continue;
            if (preferenzen.find(j) == preferenzen.end()){
                try{
                    name_sorte = obst_aliasse.left.at(j);
                } catch(...){
                    name_sorte = "Unbekannt";
                }
                cout << (ROT + name_sorte + RESET + " ");
            }
            else cout << (obst_aliasse.left.at(j) + " ");
        }
        cout << "\n";
    }
}