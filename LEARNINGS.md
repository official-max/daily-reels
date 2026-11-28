# Seekh (dono channel ke liye)

Kanha Ki Paheli ke asli numbers se seekha hua, taaki Pushpak Katha mein bhi wahi galti na ho.
Har nayi seekh tareekh ke saath upar judegi.

## 2026-11-28: pehle 19 video (21-27 Nov)

Data: YouTube Studio export (30 Oct - 27 Nov) aur public view counts.

| Kya dekha | Number |
|---|---|
| Swipe away (aage sarka diya) | **78.4%** |
| Retention | Pehle ~3 sec sab rukte hain, ~10 sec tak 85% chale jaate hain, uske baad jo bache wo lagbhag poori dekhte hain |
| Average dekhna | 16 sec (video ~56 sec) |
| Krishna katha | 113-222 views |
| Paheli | 15-98 views |
| 26 Nov ke baad | Nayi video sirf 9-24 baar dikhi (impressions), par jinhone dekhi unhone poori dekhi |

**Seekh**
1. **Pehle 2-3 second sab kuch hain.** Shuru mein koi bada title card nahi. Pehle frame se drishya, pehli line mein takraav, sawaal ya jhatka.
2. **Pehle 10 sec mein har shot mein kuch hona chahiye.**
3. **Krishna aur bhakti ki kahaniyan** is audience ko paheli se 2-3 guna pasand hain.
4. **"Part 2" title se nuksaan nahi dikha** (do sabse zyada views wali video Part 2 thi).
5. **Ek jaisi video lagaatar aane par** YouTube nayi video dikhana kam kar deta hai. Har kahani ka look alag ho.
6. **Samay (12/4/7) wajah nahi tha.** Giravat har slot mein ek saath aayi.
7. **Naam ya handle baar-baar mat badlo.** Badlaav ke baad 1-2 hafte rukkar numbers dekho.

**Kiya (Kanha Ki Paheli)**
- Bada title card band (`reels/render.py`, `SHOW_TITLE = False`)
- 2 Krishna series, phir 1 paheli (`reels/pipeline.py`, `next_kind`)
- Writer ko niyam: pehli line 2 sec mein hook, "Ek baar ki baat hai" nahi, Part 2+ ka recap naye dekhne wale ke liye bhi hook ho

**Pushpak Katha mein lagana**
- Har bhaag pehle frame se action ya rahasya se shuru ho (bhaag 1: Ravan aur Meghnad ki parchhai)
- Title chhota aur upar ho, drishya ko na dhake
- Har bhaag mein naye drishya aur kirdaar ho (factory)

**Agli jaanch:** 5 Dec 2026 ke aas-paas, naye niyam wali video ka swipe % aur views dekhna.
